"""
Interactive HTML report generator using Chart.js for visualizations.

Creates comprehensive HTML reports with embedded interactive charts
for enhancer detection analysis results.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime
import json


class ChartJSReportGenerator:
    """Generate interactive HTML reports with Chart.js visualizations."""
    
    def __init__(self, output_dir: str = "data/enhancer_outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_html_report(
        self,
        results: List[Dict[str, Any]],
        gene: str,
        cancer_type: str,
        research_question: str,
        genome_build: str = "hg38",
        tissue_type: str = "Unknown"
    ) -> str:
        """
        Generate comprehensive HTML report with Chart.js visualizations.
        
        Args:
            results: List of mutation analysis results
            gene: Gene name
            cancer_type: Cancer type
            research_question: Research question being investigated
            
        Returns:
            Path to generated HTML report
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.output_dir / f"enhancer_report_{timestamp}.html"
        
        # Generate HTML content
        html_content = self._generate_html_content(
            results, gene, cancer_type, research_question, timestamp,
            genome_build, tissue_type
        )
        
        # Write HTML file
        report_path.write_text(html_content)
        return str(report_path)
    
    def _generate_html_content(
        self,
        results: List[Dict[str, Any]],
        gene: str,
        cancer_type: str,
        research_question: str,
        timestamp: str,
        genome_build: str = "hg38",
        tissue_type: str = "Unknown"
    ) -> str:
        """Generate the complete HTML content with embedded Chart.js."""
        
        # Calculate summary statistics
        total_mutations = len(results)
        successful_analyses = sum(1 for r in results if r.get('status') == 'success')
        enhancer_detected = sum(1 for r in results if r.get('enhancer_detected', False))
        detection_rate = enhancer_detected / successful_analyses if successful_analyses > 0 else 0
        
        # Generate charts data
        charts_data = self._prepare_charts_data(results)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhancer Detection Report - {gene} in {cancer_type}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --text-primary: #222222;
            --text-secondary: #717171;
            --text-muted: #b0b0b0;
            --bg-primary: #ffffff;
            --border-light: #ebebeb;
            --shadow-subtle: 0 1px 2px rgba(0, 0, 0, 0.04);
            --shadow-hover: 0 4px 8px rgba(0, 0, 0, 0.08);
            --shadow-card: 0 2px 8px rgba(0, 0, 0, 0.04);
            --accent-green: #00a699;
            --accent-red: #ff5a5f;
            --accent-yellow: #ffb400;
            --accent-blue: #008489;
        }}
        
        body {{
            font-family: 'Circular', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            line-height: 1.5;
            color: var(--text-primary);
            background: var(--bg-primary);
            font-size: 14px;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        
        .container {{
            max-width: 1280px;
            margin: 0 auto;
            padding: 0 24px;
        }}
        
        .header {{
            padding: 64px 0 48px;
            border-bottom: 1px solid var(--border-light);
        }}
        
        .header-badge {{
            display: inline-flex;
            align-items: center;
            background: #f7f7f7;
            color: var(--text-secondary);
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            margin-bottom: 24px;
        }}
        
        .header h1 {{
            font-size: 48px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 16px;
            letter-spacing: -1px;
            line-height: 1.1;
        }}
        
        .header .subtitle {{
            font-size: 24px;
            color: var(--text-secondary);
            font-weight: 400;
            margin-bottom: 8px;
        }}
        
        .header .research-question {{
            font-size: 16px;
            color: var(--text-muted);
            margin-top: 24px;
        }}
        
        .header .metadata-info {{
            font-size: 14px;
            color: var(--text-secondary);
            margin-top: 12px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .header .metadata-info .separator {{
            color: var(--border-light);
        }}
        
        .metrics-section {{
            padding: 48px 0;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 24px;
        }}
        
        .metric-card {{
            background: var(--bg-primary);
            padding: 32px;
            border-radius: 12px;
            transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            cursor: pointer;
            display: flex;
            align-items: flex-start;
            gap: 20px;
            box-shadow: var(--shadow-card);
        }}
        
        .metric-card:hover {{
            box-shadow: var(--shadow-hover);
            transform: translateY(-4px);
        }}
        
        .metric-icon {{
            width: 48px;
            height: 48px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            flex-shrink: 0;
        }}
        
        .metric-icon.total {{
            background: rgba(0, 166, 153, 0.1);
            color: var(--accent-green);
        }}
        
        .metric-icon.success {{
            background: rgba(0, 132, 137, 0.1);
            color: var(--accent-blue);
        }}
        
        .metric-icon.detected {{
            background: rgba(255, 90, 95, 0.1);
            color: var(--accent-red);
        }}
        
        .metric-icon.rate {{
            background: rgba(255, 180, 0, 0.1);
            color: var(--accent-yellow);
        }}
        
        .metric-content {{
            flex: 1;
        }}
        
        .metric-value {{
            font-size: 32px;
            font-weight: 600;
            color: var(--text-primary);
            line-height: 1;
            margin-bottom: 4px;
        }}
        
        .metric-label {{
            font-size: 14px;
            color: var(--text-secondary);
            font-weight: 400;
        }}
        
        .methodology-section {{
            padding: 48px 0;
            border-top: 1px solid var(--border-light);
        }}
        
        .methodology-content {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 24px;
            margin-top: 20px;
        }}
        
        .methodology-item {{
            display: flex;
            align-items: flex-start;
            gap: 12px;
        }}
        
        .methodology-icon {{
            width: 24px;
            height: 24px;
            background: rgba(0, 166, 153, 0.1);
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--accent-green);
            font-size: 14px;
            font-weight: 600;
            flex-shrink: 0;
            margin-top: 2px;
        }}
        
        .methodology-text {{
            font-size: 14px;
            color: var(--text-secondary);
            line-height: 1.5;
        }}
        
        .section-title {{
            font-size: 20px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 24px;
            letter-spacing: -0.3px;
        }}
        
        .mutation-analysis {{
            padding: 48px 0;
            border-top: 1px solid var(--border-light);
        }}
        
        .mutation-card {{
            background: var(--bg-primary);
            border-radius: 12px;
            margin-bottom: 32px;
            overflow: hidden;
            transition: box-shadow 0.3s ease;
            box-shadow: var(--shadow-card);
        }}
        
        .mutation-card:hover {{
            box-shadow: var(--shadow-hover);
        }}
        
        .mutation-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 24px 32px;
            background: var(--bg-primary);
            border-bottom: 1px solid var(--border-light);
        }}
        
        .mutation-id {{
            font-size: 16px;
            font-weight: 600;
            color: var(--text-primary);
            font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
        }}
        
        .detection-badge {{
            padding: 6px 14px;
            border-radius: 16px;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.3px;
            text-transform: uppercase;
        }}
        
        .detected {{
            background: rgba(0, 166, 153, 0.1);
            color: var(--accent-green);
        }}
        
        .not-detected {{
            background: rgba(113, 113, 113, 0.1);
            color: var(--text-secondary);
        }}
        
        .mutation-content {{
            padding: 24px;
        }}
        
        .genomic-position {{
            background: #f7f7f7;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }}
        
        .position-label {{
            font-size: 12px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-right: 12px;
        }}
        
        .position-value {{
            font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
            font-size: 14px;
            font-weight: 500;
            color: var(--accent-red);
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 16px;
            margin-bottom: 24px;
        }}
        
        .chart-container {{
            background: #fafafa;
            border-radius: 8px;
            padding: 24px;
            position: relative;
            height: 400px;
        }}
        
        .evidence-section {{
            background: #fafafa;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 32px;
        }}
        
        .evidence-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
            margin-top: 16px;
        }}
        
        .evidence-item {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            background: var(--bg-primary);
            border-radius: 8px;
            font-size: 14px;
            box-shadow: var(--shadow-subtle);
        }}
        
        .evidence-icon {{
            width: 32px;
            height: 32px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            flex-shrink: 0;
        }}
        
        .evidence-positive {{
            background: rgba(0, 166, 153, 0.1);
            color: var(--accent-green);
        }}
        
        .evidence-negative {{
            background: rgba(113, 113, 113, 0.1);
            color: var(--text-secondary);
        }}
        
        .decision-section {{
            background: var(--bg-primary);
            border-radius: 8px;
            padding: 32px;
            margin-top: 24px;
        }}
        
        .decision-header {{
            font-size: 16px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .algorithm-badge {{
            background: #f7f7f7;
            padding: 16px 20px;
            border-radius: 8px;
            margin-bottom: 24px;
        }}
        
        .algorithm-badge h4 {{
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-muted);
            margin-bottom: 4px;
            font-weight: 600;
        }}
        
        .algorithm-badge p {{
            font-size: 14px;
            color: var(--text-secondary);
            line-height: 1.5;
        }}
        
        .criteria-table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin: 24px 0;
            font-size: 14px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: var(--shadow-subtle);
        }}
        
        .criteria-table th {{
            background: #f7f7f7;
            padding: 16px;
            text-align: left;
            font-weight: 600;
            color: var(--text-secondary);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid var(--border-light);
        }}
        
        .criteria-table td {{
            padding: 16px;
            border-bottom: 1px solid var(--border-light);
            color: var(--text-primary);
            background: var(--bg-primary);
        }}
        
        .criteria-table tr:last-child td {{
            border-bottom: none;
        }}
        
        .criteria-pass {{
            color: var(--accent-green);
            font-weight: 600;
        }}
        
        .criteria-fail {{
            color: var(--text-muted);
            font-weight: 400;
        }}
        
        .score-section {{
            background: #fafafa;
            border-radius: 8px;
            padding: 20px;
            margin: 24px 0;
        }}
        
        .score-label {{
            font-size: 14px;
            color: var(--text-secondary);
            margin-bottom: 8px;
            font-weight: 500;
        }}
        
        .score-bar {{
            width: 100%;
            height: 6px;
            background: #e5e5e5;
            border-radius: 3px;
            overflow: hidden;
        }}
        
        .score-fill {{
            height: 100%;
            background: var(--accent-green);
            transition: width 0.3s ease;
        }}
        
        .biological-context {{
            background: #f7f7f7;
            border-left: 3px solid var(--accent-green);
            padding: 20px;
            margin: 24px 0;
            border-radius: 0 8px 8px 0;
            font-size: 14px;
            color: var(--text-secondary);
            line-height: 1.6;
        }}
        
        .footer {{
            padding: 48px 0;
            text-align: center;
            border-top: 1px solid var(--border-light);
            margin-top: 64px;
        }}
        
        .footer-text {{
            font-size: 13px;
            color: var(--text-muted);
            margin-bottom: 4px;
        }}
        
        .footer-brand {{
            font-size: 14px;
            color: var(--text-secondary);
            font-weight: 500;
            margin-top: 12px;
        }}
        
        /* Subtle animations */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .mutation-card {{
            animation: fadeIn 0.3s ease;
        }}
        
        /* Responsive design */
        @media (max-width: 768px) {{
            .container {{
                margin: 20px;
                border-radius: 8px;
            }}
            
            .header {{
                padding: 32px 24px;
            }}
            
            .metrics-grid {{
                padding: 24px;
                gap: 16px;
            }}
            
            .mutation-analysis {{
                padding: 24px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="header-badge">AlphaGenome Analysis</span>
            <h1>Enhancer Detection Report</h1>
            <div class="subtitle">{gene} mutations in {cancer_type} cancer</div>
            <div class="research-question">Research Question: {research_question}</div>
            <div class="metadata-info">
                <span>Genome Build: {genome_build}</span>
                <span class="separator">•</span>
                <span>Tissue: {tissue_type}</span>
                <span class="separator">•</span>
                <span>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span>
            </div>
        </div>
        
        <div class="metrics-section">
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-icon total">🧬</div>
                    <div class="metric-content">
                        <div class="metric-value">{total_mutations}</div>
                        <div class="metric-label">Total Mutations</div>
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon success">✓</div>
                    <div class="metric-content">
                        <div class="metric-value">{successful_analyses}</div>
                        <div class="metric-label">Successful Analyses</div>
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon detected">🎯</div>
                    <div class="metric-content">
                        <div class="metric-value">{enhancer_detected}</div>
                        <div class="metric-label">Enhancers Detected</div>
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon rate">📊</div>
                    <div class="metric-content">
                        <div class="metric-value">{detection_rate:.1%}</div>
                        <div class="metric-label">Detection Rate</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!--<div class="methodology-section">
            <h2 class="section-title">Methodology</h2>
            <div class="methodology-content">
                <div class="methodology-item">
                    <div class="methodology-icon">✓</div>
                    <div class="methodology-text">Real-time mutation data from cBioPortal</div>
                </div>
                <div class="methodology-item">
                    <div class="methodology-icon">✓</div>
                    <div class="methodology-text">AlphaGenome API for regulatory predictions</div>
                </div>
                <div class="methodology-item">
                    <div class="methodology-icon">✓</div>
                    <div class="methodology-text">ENCODE-based detection algorithms</div>
                </div>
                <div class="methodology-item">
                    <div class="methodology-icon">✓</div>
                    <div class="methodology-text">Tissue-specific threshold adjustments</div>
                </div>
                <div class="methodology-item">
                    <div class="methodology-icon">✓</div>
                    <div class="methodology-text">Interactive Chart.js visualizations</div>
                </div>
            </div>
        </div>-->
        
        <div class="mutation-analysis">
            <h2 class="section-title">Detailed Mutation Analysis</h2>
            {self._generate_mutation_cards(results)}
        </div>
        
        <div class="footer">
            <div class="footer-text">Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
            <div class="footer-brand">AlphaGenome Cancer Research Pipeline v2.0</div>
            <div class="footer-text">Powered by cBioPortal + AlphaGenome API</div>
        </div>
    </div>
    
    <script>
        // Chart.js data
        const chartsData = {json.dumps(charts_data)};
        
        // Initialize all charts
        document.addEventListener('DOMContentLoaded', function() {{
            initializeCharts();
        }});
        
        function initializeCharts() {{
            // Initialize charts for each mutation
            Object.keys(chartsData).forEach(mutationId => {{
                const data = chartsData[mutationId];
                if (data && data.tracks) {{
                    createTracksCharts(mutationId, data.tracks);
                }}
            }});
        }}
        
        function createTracksCharts(mutationId, tracks) {{
            Object.keys(tracks).forEach(trackName => {{
                const trackData = tracks[trackName];
                createTrackChart(mutationId, trackName, trackData);
            }});
        }}
        
        function createTrackChart(mutationId, trackName, trackData) {{
            const canvasId = `chart-${{mutationId}}-${{trackName}}`;
            const canvas = document.getElementById(canvasId);
            
            if (!canvas || !trackData.ref || !trackData.alt) return;
            
            // Calculate fold change (ALT / REF) - this shows relative differences much better
            const foldChange = trackData.alt.map((alt, i) => {{
                const ref = trackData.ref[i] || 0.000001;
                if (ref === 0) return 1; // If ref is 0, fold change is undefined, use 1
                return alt / ref;
            }});
            
            // Calculate percentage difference for better interpretation
            const percentDiff = trackData.alt.map((alt, i) => {{
                const ref = trackData.ref[i] || 0.000001;
                if (ref === 0) return 0;
                return ((alt - ref) / ref) * 100;
            }});
            
            // Calculate absolute difference
            const absoluteDiff = trackData.alt.map((alt, i) => alt - (trackData.ref[i] || 0));
            
            new Chart(canvas, {{
                type: 'line',
                data: {{
                    labels: Array.from({{length: trackData.ref.length}}, (_, i) => i),
                    datasets: [
                        {{
                            label: 'Reference Signal',
                            data: trackData.ref,
                            borderColor: '#717171',
                            backgroundColor: 'rgba(113, 113, 113, 0.05)',
                            fill: false,
                            tension: 0.2,
                            pointRadius: 0,
                            borderWidth: 2,
                            yAxisID: 'y'
                        }},
                        {{
                            label: 'Mutation Signal',
                            data: trackData.alt,
                            borderColor: '#ff5a5f',
                            backgroundColor: 'rgba(255, 90, 95, 0.05)',
                            fill: false,
                            tension: 0.2,
                            pointRadius: 0,
                            borderWidth: 2,
                            yAxisID: 'y'
                        }},
                        {{
                            label: 'Fold Change (Mut/Ref)',
                            data: foldChange,
                            borderColor: '#ffb400',
                            backgroundColor: 'rgba(255, 180, 0, 0.05)',
                            fill: false,
                            tension: 0.2,
                            pointRadius: 0,
                            borderWidth: 2,
                            borderDash: [6, 3],
                            yAxisID: 'y1'
                        }},
                        {{
                            label: 'Difference (Mut - Ref)',
                            data: absoluteDiff,
                            borderColor: '#00a699',
                            backgroundColor: 'rgba(0, 166, 153, 0.05)',
                            fill: false,
                            tension: 0.2,
                            pointRadius: 0,
                            borderWidth: 2,
                            yAxisID: 'y2'
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{
                        intersect: false,
                        mode: 'index'
                    }},
                    plugins: {{
                        legend: {{
                            display: true,
                            position: 'top',
                            labels: {{
                                usePointStyle: true,
                                padding: 15,
                                font: {{
                                    size: 12,
                                    family: "'Inter', sans-serif"
                                }}
                            }},
                            onClick: (e, legendItem, legend) => {{
                                const index = legendItem.datasetIndex;
                                const ci = legend.chart;
                                const meta = ci.getDatasetMeta(index);
                                meta.hidden = meta.hidden === null ? !ci.data.datasets[index].hidden : null;
                                ci.update();
                            }}
                        }},
                        title: {{
                            display: true,
                            text: `${{trackName}} Track Analysis`,
                            font: {{
                                size: 14,
                                family: "'Inter', sans-serif",
                                weight: '600'
                            }},
                            color: '#222222',
                            padding: {{
                                bottom: 15
                            }}
                        }},
                        tooltip: {{
                            backgroundColor: 'rgba(255, 255, 255, 0.98)',
                            borderColor: '#ebebeb',
                            borderWidth: 1,
                            titleColor: '#222222',
                            bodyColor: '#717171',
                            titleFont: {{
                                size: 13,
                                weight: '600'
                            }},
                            bodyFont: {{
                                size: 12
                            }},
                            padding: 12,
                            cornerRadius: 6,
                            callbacks: {{
                                label: function(context) {{
                                    let label = context.dataset.label || '';
                                    if (label) {{
                                        label += ': ';
                                    }}
                                    const value = context.parsed.y;
                                    
                                    if (context.datasetIndex === 2) {{ // Fold change
                                        return label + value.toFixed(3) + 'x';
                                    }} else if (context.datasetIndex === 3) {{ // Difference
                                        return label + value.toExponential(3);
                                    }} else {{ // Raw signals
                                        return label + value.toExponential(3);
                                    }}
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            display: true,
                            grid: {{
                                color: '#fafafa',
                                drawBorder: false
                            }},
                            ticks: {{
                                color: '#b0b0b0',
                                font: {{
                                    size: 11
                                }}
                            }},
                            title: {{
                                display: true,
                                text: 'Genomic Position',
                                color: '#717171',
                                font: {{
                                    size: 12
                                }}
                            }}
                        }},
                        y: {{
                            type: 'logarithmic',
                            display: true,
                            position: 'left',
                            grid: {{
                                color: '#f8f9fa',
                                drawBorder: false
                            }},
                            title: {{
                                display: true,
                                text: 'Signal Intensity (log)',
                                color: '#6c757d',
                                font: {{
                                    size: 12
                                }}
                            }},
                            ticks: {{
                                color: '#6c757d',
                                font: {{
                                    size: 11
                                }},
                                callback: function(value) {{
                                    if (value < 0.001) return value.toExponential(1);
                                    return value.toFixed(4);
                                }}
                            }}
                        }},
                        y1: {{
                            type: 'linear',
                            display: true,
                            position: 'right',
                            grid: {{
                                drawOnChartArea: false,
                                drawBorder: false
                            }},
                            title: {{
                                display: true,
                                text: 'Fold Change',
                                color: '#f59e0b',
                                font: {{
                                    size: 12
                                }}
                            }},
                            ticks: {{
                                color: '#f59e0b',
                                font: {{
                                    size: 11
                                }},
                                callback: function(value) {{
                                    return value.toFixed(2) + 'x';
                                }}
                            }},
                            suggestedMin: 0.5,
                            suggestedMax: 2.0
                        }},
                        y2: {{
                            type: 'linear',
                            display: 'auto',
                            position: 'right',
                            grid: {{
                                drawOnChartArea: false,
                                drawBorder: false
                            }},
                            title: {{
                                display: true,
                                text: 'Difference',
                                color: '#10a37f',
                                font: {{
                                    size: 12
                                }}
                            }},
                            ticks: {{
                                color: '#10a37f',
                                font: {{
                                    size: 11
                                }},
                                callback: function(value) {{
                                    return value.toExponential(1);
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        }}
    </script>
</body>
</html>"""
        
        return html
    
    def _generate_mutation_cards(self, results: List[Dict[str, Any]]) -> str:
        """Generate HTML for individual mutation cards."""
        cards_html = []
        
        for result in results:
            if result.get('status') != 'success':
                continue
            
            variant_id = result.get('variant_id', 'Unknown')
            enhancer_detected = result.get('enhancer_detected', False)
            detection_result = result.get('detection_result', {})
            
            if not isinstance(detection_result, dict):
                detection_result = {}
            
            prof_detection = detection_result.get('professional_detection', {})
            
            # Safe ID for HTML elements
            safe_id = variant_id.replace(':', '-').replace('>', '-')
            
            # Detection badge
            badge_class = 'detected' if enhancer_detected else 'not-detected'
            badge_text = 'Enhancer Detected' if enhancer_detected else 'No Enhancer'
            
            # Evidence items
            evidence_html = self._generate_evidence_html(prof_detection)
            
            # Charts grid
            charts_html = self._generate_charts_grid_html(safe_id, result)
            
            # Decision rationale
            rationale_html = self._generate_decision_rationale(detection_result, result.get('alphagenome_result', {}))
            
            card_html = f"""
            <div class="mutation-card">
                <div class="mutation-header">
                    <div class="mutation-id">{self._format_variant_id(variant_id)}</div>
                    <div class="detection-badge {badge_class}">{badge_text}</div>
                </div>
                
                <div class="mutation-content">
                    <div class="genomic-position">
                        <span class="position-label">Variant Position</span>
                        <span class="position-value">{self._format_variant_id(variant_id)}</span>
                    </div>
                    
                    {charts_html}
                    
                    <div class="evidence-section">
                        <h3 style="font-size: 16px; font-weight: 600; color: var(--text-primary); margin-bottom: 16px;">Evidence Summary</h3>
                        <div class="evidence-grid">
                            {evidence_html}
                        </div>
                    </div>
                    
                    <div class="decision-section">
                        {rationale_html}
                    </div>
                </div>
            </div>
            """
            
            cards_html.append(card_html)
        
        return '\n'.join(cards_html)
    
    def _generate_evidence_html(self, prof_detection: Dict[str, Any]) -> str:
        """Generate HTML for evidence items."""
        positive_marks = prof_detection.get('positive_marks', [])
        confidence = prof_detection.get('confidence', 'unknown')
        score = prof_detection.get('total_evidence_score', 0)
        
        evidence_items = []
        
        # Add positive marks
        for mark in positive_marks[:5]:
            mark_display = mark.replace('_', ' ').title()
            evidence_items.append(f"""
                <div class="evidence-item">
                    <div class="evidence-icon evidence-positive">✓</div>
                    <div style="font-size: 13px; color: var(--text-secondary);">{mark_display}</div>
                </div>
            """)
        
        # Add confidence badge
        confidence_color = '#10a37f' if confidence == 'high' else '#f59e0b' if confidence == 'medium' else '#6c757d'
        evidence_items.append(f"""
            <div class="evidence-item">
                <div class="evidence-icon" style="background: rgba(16, 163, 127, 0.1); color: {confidence_color};">★</div>
                <div style="font-size: 13px;">
                    <span style="color: var(--text-muted);">Confidence:</span> 
                    <strong style="color: {confidence_color};">{confidence.upper()}</strong>
                </div>
            </div>
        """)
        
        # Add score
        evidence_items.append(f"""
            <div class="evidence-item">
                <div class="evidence-icon" style="background: var(--bg-tertiary); color: var(--primary-color);">⚡</div>
                <div style="font-size: 13px;">
                    <span style="color: var(--text-muted);">Score:</span> 
                    <strong style="color: var(--text-primary);">{score:.1f}/10</strong>
                </div>
            </div>
        """)
        
        return '\n'.join(evidence_items)
    
    def _generate_decision_rationale(self, detection_result: Dict[str, Any], alphagenome_result: Dict[str, Any]) -> str:
        """Generate comprehensive decision rationale explaining enhancer detection."""
        # Handle case where detection_result might not be a dict
        if not isinstance(detection_result, dict):
            return f"""
            <div class="decision-rationale">
                <h3 style="color: #dc3545;">⚠️ Decision Data Unavailable</h3>
                <p>Unable to generate detailed rationale - detection result format issue.</p>
                <p>Raw data: {detection_result}</p>
            </div>
            """
        
        prof_detection = detection_result.get('professional_detection', {})
        legacy_detection = detection_result.get('legacy_detection', {})
        
        is_enhancer = prof_detection.get('is_enhancer_like', False)
        confidence = prof_detection.get('confidence', 'unknown')
        algorithm = prof_detection.get('algorithm_used', 'unknown')
        criteria_used = prof_detection.get('criteria_used', {})
        evidence_scores = prof_detection.get('evidence_scores', {})
        total_score = prof_detection.get('total_evidence_score', 0)
        positive_marks = prof_detection.get('positive_marks', [])
        
        # Algorithm information
        algorithm_descriptions = {
            'conservative': 'High specificity - requires strong evidence across multiple marks to avoid false positives',
            'balanced': 'Balanced sensitivity and specificity - standard ENCODE-based thresholds',
            'sensitive': 'High sensitivity - detects weaker enhancer signatures that might be missed by conservative approaches'
        }
        
        algorithm_info = f"""
        <div class="algorithm-badge">
            <h4>Detection Algorithm</h4>
            <p><strong>{algorithm.title()}</strong> - {algorithm_descriptions.get(algorithm.lower(), 'Unknown algorithm')}</p>
        </div>
        """
        
        # Criteria evaluation table
        criteria_table = self._generate_criteria_table(evidence_scores, criteria_used, alphagenome_result)
        
        # Score breakdown
        score_percentage = min(100, (total_score / 10) * 100)
        score_bar = f"""
        <div style="margin: 15px 0;">
            <strong>Overall Evidence Score: {total_score:.1f}/10 ({score_percentage:.1f}%)</strong>
            <div class="score-bar">
                <div class="score-fill" style="width: {score_percentage}%;"></div>
            </div>
        </div>
        """
        
        # Decision explanation
        decision_color = '#28a745' if is_enhancer else '#dc3545'
        decision_icon = '✅' if is_enhancer else '❌'
        
        decision_explanation = self._generate_decision_explanation(
            is_enhancer, confidence, positive_marks, total_score, algorithm
        )
        
        # Biological context
        biological_context = self._generate_biological_context(positive_marks, evidence_scores)
        
        return f"""
            <div class="decision-header">
                <span style="color: {decision_color}; font-size: 18px;">{decision_icon}</span>
                Decision Analysis
            </div>
            
            {algorithm_info}
            
            <h4 style="font-size: 14px; font-weight: 600; color: var(--text-primary); margin: 20px 0 12px 0; text-transform: uppercase; letter-spacing: 0.5px;">
                Criteria Evaluation
            </h4>
            {criteria_table}
            
            <div class="score-section">
                <div class="score-label">Overall Evidence Score: {total_score:.1f}/10</div>
                <div class="score-bar">
                    <div class="score-fill" style="width: {score_percentage}%;"></div>
                </div>
            </div>
            
            <h4 style="font-size: 14px; font-weight: 600; color: var(--text-primary); margin: 20px 0 12px 0; text-transform: uppercase; letter-spacing: 0.5px;">
                Biological Interpretation
            </h4>
            {biological_context}
            
            <h4 style="font-size: 14px; font-weight: 600; color: var(--text-primary); margin: 20px 0 12px 0; text-transform: uppercase; letter-spacing: 0.5px;">
                Final Decision
            </h4>
            <div style="background: var(--bg-tertiary); padding: 16px; border-radius: 6px; border-left: 3px solid {decision_color}; font-size: 14px; line-height: 1.6; color: var(--text-secondary);">
                {decision_explanation}
            </div>
        """
    
    def _generate_criteria_table(self, evidence_scores: Dict[str, float], criteria_used: Dict[str, Any], alphagenome_result: Dict[str, Any]) -> str:
        """Generate table showing each criterion evaluation."""
        summary = alphagenome_result.get('summary', {})
        
        # Get actual values from AlphaGenome
        dnase_increase = summary.get('dnase', {}).get('max_increase', 0)
        rna_increase = summary.get('rna_seq', {}).get('max_increase', 0)
        histone_marks = summary.get('chip_histone', {}).get('marks', {})
        
        h3k27ac_increase = histone_marks.get('H3K27ac', {}).get('max_increase', 0)
        h3k4me1_increase = histone_marks.get('H3K4me1', {}).get('max_increase', 0)
        h3k4me3_increase = histone_marks.get('H3K4me3', {}).get('max_increase', 0)
        
        # Handle case where criteria_used is a string instead of dict
        if isinstance(criteria_used, str):
            criteria_dict = {}
        else:
            criteria_dict = criteria_used or {}
        
        criteria = [
            {
                'mark': 'DNase-seq',
                'description': 'Chromatin accessibility',
                'threshold': criteria_dict.get('dnase_threshold', 0.01),
                'actual': dnase_increase,
                'score': evidence_scores.get('dnase', 0),
                'biological': 'Open chromatin regions where transcription factors can bind'
            },
            {
                'mark': 'H3K27ac',
                'description': 'Active enhancer mark',
                'threshold': criteria_dict.get('h3k27ac_threshold', 0.1),
                'actual': h3k27ac_increase,
                'score': evidence_scores.get('h3k27ac', 0),
                'biological': 'Histone modification marking active regulatory elements'
            },
            {
                'mark': 'H3K4me1',
                'description': 'Enhancer mark',
                'threshold': criteria_dict.get('h3k4me1_threshold', 0.05),
                'actual': h3k4me1_increase,
                'score': evidence_scores.get('h3k4me1', 0),
                'biological': 'Monomethylation marking enhancer regions'
            },
            {
                'mark': 'H3K4me3',
                'description': 'Promoter mark',
                'threshold': criteria_dict.get('h3k4me3_threshold', 0.1),
                'actual': h3k4me3_increase,
                'score': evidence_scores.get('h3k4me3', 0),
                'biological': 'Trimethylation typically found at active promoters'
            },
            {
                'mark': 'RNA-seq',
                'description': 'Transcriptional activity',
                'threshold': criteria_dict.get('rna_threshold', 0.001),
                'actual': rna_increase,
                'score': evidence_scores.get('rna', 0),
                'biological': 'Direct measurement of transcriptional output'
            }
        ]
        
        table_rows = []
        for criterion in criteria:
            passed = criterion['actual'] >= criterion['threshold']
            pass_class = 'criteria-pass' if passed else 'criteria-fail'
            pass_text = '✓' if passed else '✗'
            
            # Calculate score for display if passing but not in evidence_scores
            display_score = criterion['score']
            if passed and display_score == 0:
                # Calculate a simple score based on how much it exceeds threshold
                if criterion['threshold'] > 0:
                    display_score = min(1.0, (criterion['actual'] / criterion['threshold'] - 1) * 0.5 + 0.5)
                else:
                    display_score = 1.0 if criterion['actual'] > 0 else 0.0
            
            table_rows.append(f"""
                <tr>
                    <td><strong>{criterion['mark']}</strong><br><small>{criterion['description']}</small></td>
                    <td>{criterion['actual']:.6f}</td>
                    <td>{criterion['threshold']:.6f}</td>
                    <td class="{pass_class}">{pass_text}</td>
                    <td>{display_score:.1f}/1.0</td>
                    <td><small>{criterion['biological']}</small></td>
                </tr>
            """)
        
        return f"""
        <table class="criteria-table">
            <thead>
                <tr>
                    <th>Chromatin Mark</th>
                    <th>Observed Change</th>
                    <th>Required Threshold</th>
                    <th>Result</th>
                    <th>Evidence Score</th>
                    <th>Biological Function</th>
                </tr>
            </thead>
            <tbody>
                {''.join(table_rows)}
            </tbody>
        </table>
        """
    
    def _generate_biological_context(self, positive_marks: List[str], evidence_scores: Dict[str, float]) -> str:
        """Generate biological interpretation of the findings."""
        mark_explanations = {
            'dnase_accessibility': 'The mutation creates more accessible chromatin, allowing transcription factors to bind more easily.',
            'h3k27ac_active_enhancer': 'Increased H3K27ac suggests the mutation activates enhancer function by promoting histone acetylation.',
            'h3k4me1_enhancer': 'H3K4me1 enhancement indicates the mutation strengthens enhancer chromatin signatures.',
            'h3k4me3_promoter': 'H3K4me3 changes suggest the mutation may affect nearby promoter activity.',
            'rna_transcription': 'Increased RNA levels demonstrate that the mutation enhances transcriptional output.'
        }
        
        if not positive_marks:
            return """
            <div class="biological-context">
                <strong>No significant enhancer signatures detected.</strong><br>
                The mutation does not appear to create or strengthen regulatory elements based on standard chromatin marks.
                This could mean: (1) the mutation is neutral for gene regulation, (2) it affects regulation in ways not captured by these marks, 
                or (3) the effect is tissue-specific and not apparent in this context.
            </div>
            """
        
        explanations = []
        for mark in positive_marks[:3]:  # Show top 3 explanations
            if mark in mark_explanations:
                score = evidence_scores.get(mark.split('_')[0], 0)
                explanations.append(f"<li><strong>{mark.replace('_', ' ').title()}:</strong> {mark_explanations[mark]} (Score: {score:.1f})</li>")
        
        return f"""
        <div class="biological-context">
            <strong>Biological Significance:</strong>
            <ul style="margin: 10px 0; padding-left: 20px;">
                {''.join(explanations)}
            </ul>
            <p><em>These chromatin signatures indicate the mutation likely creates or strengthens a regulatory element 
            that can influence gene expression in this genomic region.</em></p>
        </div>
        """
    
    def _generate_decision_explanation(self, is_enhancer: bool, confidence: str, positive_marks: List[str], 
                                     total_score: float, algorithm: str) -> str:
        """Generate final decision explanation in plain language."""
        if is_enhancer:
            marks_display = ', '.join([m.replace('_', ' ').title() for m in positive_marks[:3]])
            explanation = f"""
            <strong style="color: var(--success-color);">ENHANCER DETECTED</strong> with <strong>{confidence.upper()}</strong> confidence<br><br>
            
            <strong>Decision Rationale:</strong><br>
            • {len(positive_marks)} out of 5 chromatin marks exceeded detection thresholds<br>
            • Evidence score: {total_score:.1f}/10 (above {algorithm} threshold)<br>
            • Key signatures: {marks_display}<br><br>
            
            <strong>Biological Significance:</strong><br>
            This mutation appears to create or strengthen a regulatory element capable of influencing gene expression. 
            The chromatin modification pattern aligns with established enhancer signatures from ENCODE consortium data.
            """
        else:
            explanation = f"""
            <strong style="color: var(--danger-color);">NO ENHANCER DETECTED</strong> with <strong>{confidence.upper()}</strong> confidence<br><br>
            
            <strong>Decision Rationale:</strong><br>
            • Only {len(positive_marks)} out of 5 chromatin marks showed significant changes<br>
            • Evidence score: {total_score:.1f}/10 (below {algorithm} threshold)<br>
            • Insufficient regulatory signatures detected<br><br>
            
            <strong>Biological Significance:</strong><br>
            This mutation does not exhibit significant regulatory activity based on standard chromatin signatures. 
            The variant may be functionally neutral or affect regulation through mechanisms not captured by these assays.
            """
        
        return explanation
    
    def _generate_charts_grid_html(self, safe_id: str, result: Dict[str, Any]) -> str:
        """Generate HTML grid for combined charts."""
        tracks = ['DNase', 'H3K27ac', 'H3K4me1', 'H3K4me3', 'RNA']
        charts = []
        
        for track in tracks:
            charts.append(f"""
                <div class="chart-container">
                    <canvas id="chart-{safe_id}-{track}"></canvas>
                </div>
            """)
        
        return f'<div class="charts-grid">{" ".join(charts)}</div>'
    
    def _downsample_array(self, data: list, target_points: int = 1000) -> list:
        """Downsample array to target number of points for visualization."""
        if len(data) <= target_points:
            return data
        
        # Simple decimation - take every nth point
        step = len(data) // target_points
        return [data[i] for i in range(0, len(data), step)][:target_points]
    
    def _prepare_charts_data(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare optimized data for Chart.js visualization."""
        charts_data = {}
        
        for result in results:
            if result.get('status') != 'success':
                continue
            
            variant_id = result.get('variant_id', 'Unknown')
            safe_id = variant_id.replace(':', '-').replace('>', '-')
            
            alphagenome_result = result.get('alphagenome_result', {})
            raw_data = alphagenome_result.get('raw', {})
            
            if not raw_data:
                continue
            
            # Extract track data with downsampling
            tracks_data = {}
            ref_outputs = raw_data.get('reference')
            alt_outputs = raw_data.get('alternate')
            
            if ref_outputs and alt_outputs:
                # DNase
                if hasattr(ref_outputs, 'dnase') and ref_outputs.dnase is not None:
                    ref_values = self._downsample_array(ref_outputs.dnase.values.flatten().tolist())
                    alt_values = self._downsample_array(alt_outputs.dnase.values.flatten().tolist())
                    delta = sum(alt_values) / len(alt_values) - sum(ref_values) / len(ref_values)
                    tracks_data['DNase'] = {
                        'ref': ref_values,
                        'alt': alt_values,
                        'delta': delta
                    }
                
                # RNA
                if hasattr(ref_outputs, 'rna_seq') and ref_outputs.rna_seq is not None:
                    ref_values = self._downsample_array(ref_outputs.rna_seq.values.flatten().tolist())
                    alt_values = self._downsample_array(alt_outputs.rna_seq.values.flatten().tolist())
                    delta = sum(alt_values) / len(alt_values) - sum(ref_values) / len(ref_values)
                    tracks_data['RNA'] = {
                        'ref': ref_values,
                        'alt': alt_values,
                        'delta': delta
                    }
                
                # Histone marks
                if hasattr(ref_outputs, 'chip_histone') and ref_outputs.chip_histone is not None:
                    ref_hist = ref_outputs.chip_histone.values
                    alt_hist = alt_outputs.chip_histone.values
                    
                    if ref_hist.size > 0 and alt_hist.size > 0:
                        # Simple positional mapping for common marks
                        mark_mapping = {0: 'H3K27ac', 1: 'H3K4me1', 2: 'H3K4me3'}
                        
                        for i, mark_name in mark_mapping.items():
                            if len(ref_hist.shape) > 1 and i < ref_hist.shape[1]:
                                ref_values = self._downsample_array(ref_hist[:, i].tolist())
                                alt_values = self._downsample_array(alt_hist[:, i].tolist())
                                delta = sum(alt_values) / len(alt_values) - sum(ref_values) / len(ref_values)
                                tracks_data[mark_name] = {
                                    'ref': ref_values,
                                    'alt': alt_values,
                                    'delta': delta
                                }
            
            charts_data[safe_id] = {
                'variant_id': variant_id,
                'tracks': tracks_data
            }
        
        return charts_data
    
    def _generate_scientific_rationale(self, scientific_detection: Dict[str, Any], alphagenome_result: Dict[str, Any]) -> str:
        """Generate scientifically rigorous decision rationale."""
        detected = scientific_detection.get('detected', False)
        state = scientific_detection.get('state', 'not_enhancer')
        confidence = scientific_detection.get('confidence', 'low')
        confidence_score = scientific_detection.get('confidence_score', 0)
        region_type = scientific_detection.get('region_type', 'unknown')
        is_coding = scientific_detection.get('is_coding', False)
        positive_evidence = scientific_detection.get('positive_evidence', [])
        missing_evidence = scientific_detection.get('missing_evidence', [])
        warnings = scientific_detection.get('warnings', [])
        interpretation = scientific_detection.get('interpretation', '')
        scores = scientific_detection.get('scores', {})
        
        # Critical warnings section
        warnings_html = ""
        if warnings:
            warning_items = "".join([f"<li>⚠️ {w}</li>" for w in warnings])
            warnings_html = f"""
            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; margin-bottom: 20px;">
                <strong>Critical Warnings:</strong>
                <ul style="margin: 8px 0 0 20px; padding: 0;">
                    {warning_items}
                </ul>
            </div>
            """
        
        # Region context
        region_context = f"""
        <div style="margin-bottom: 16px;">
            <strong>Genomic Context:</strong> {region_type.replace('_', ' ').title()}
            {' (Coding variant)' if is_coding else ''}
        </div>
        """
        
        # Detection result
        if not detected:
            result_color = "#dc3545"
            result_text = "NO ENHANCER DETECTED"
            result_explanation = f"""
            <p><strong>Conclusion:</strong> {interpretation}</p>
            <p><strong>Missing Required Evidence:</strong></p>
            <ul style="margin: 8px 0 0 20px;">
                {"".join([f"<li>{e}</li>" for e in missing_evidence])}
            </ul>
            """
        else:
            result_color = "#28a745" if confidence == "high" else "#ffc107" if confidence == "medium" else "#fd7e14"
            result_text = f"ENHANCER {state.upper()} DETECTED"
            result_explanation = f"""
            <p><strong>Conclusion:</strong> {interpretation}</p>
            <p><strong>Confidence:</strong> {confidence.upper()} (Score: {confidence_score:.2f})</p>
            <p><strong>Supporting Evidence:</strong></p>
            <ul style="margin: 8px 0 0 20px;">
                {"".join([f"<li>✓ {e}</li>" for e in positive_evidence])}
            </ul>
            """
        
        # Scores breakdown
        scores_html = f"""
        <div style="margin-top: 16px; padding: 12px; background: #f8f9fa; border-radius: 4px;">
            <strong>Evidence Scores:</strong>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-top: 8px;">
                <div>Histone Marks: {scores.get('histone', 0):.2f}</div>
                <div>Accessibility: {scores.get('accessibility', 0):.2f}</div>
                <div>RNA Signal: {scores.get('rna', 0):.2f}</div>
                <div>Statistical: {scores.get('statistical', 0):.2f}</div>
            </div>
        </div>
        """
        
        # Scientific note
        scientific_note = """
        <div style="margin-top: 20px; padding: 12px; background: #e7f3ff; border-left: 4px solid #0066cc;">
            <small><strong>Note:</strong> This analysis uses strict scientific criteria requiring H3K4me1 and H3K27ac 
            enrichment for active enhancer detection. Coding variants in exons are excluded from enhancer calling 
            per scientific consensus.</small>
        </div>
        """
        
        return f"""
        <div class="decision-rationale">
            <h3 style="color: {result_color};">{result_text}</h3>
            {warnings_html}
            {region_context}
            {result_explanation}
            {scores_html}
            {scientific_note}
        </div>
        """
    
    def _format_variant_id(self, variant_id: str) -> str:
        """Format variant ID to prevent duplicates and improve readability."""
        if not variant_id or variant_id == "Unknown":
            return "Unknown"
        
        # Handle the case where variant_id might be duplicated like "chr12:25398285:C>Gchr12..."
        # Just take the first occurrence
        if variant_id.count("chr") > 1:
            # Find the position where the second "chr" starts
            first_chr_end = variant_id.find("chr", 3)  # Start search after first "chr"
            if first_chr_end > 0:
                variant_id = variant_id[:first_chr_end]
        
        return variant_id