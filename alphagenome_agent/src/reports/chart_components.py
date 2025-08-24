"""
Reusable Chart.js components for genomic visualization reports.

This module provides modular, reusable chart components that can be
integrated into various genomic analysis reports.
"""

from typing import Dict, List, Any, Optional
import json


class TabbedChartComponent:
    """
    A reusable tabbed chart component for displaying multiple genomic tracks.
    
    Features:
    - Tab navigation for switching between different data tracks
    - Explanatory text for each track type
    - Responsive design with mobile support
    - Clean, minimalistic Airbnb-inspired aesthetic
    """
    
    # Track definitions with metadata
    TRACK_DEFINITIONS = {
        'EnhancerProbability': {
            'label': 'Enhancer Probability',
            'icon': '📈',
            'color': '#008489',
            'description': 'Computed enhancer probability combining multiple genomic signals. Shows the likelihood of enhancer activity at each position, with confidence intervals indicating prediction uncertainty.'
        },
        'DNase': {
            'label': 'Chromatin Accessibility',
            'icon': '🔓',
            'color': '#ff9500',
            'description': 'Shows open chromatin regions where DNA is accessible to regulatory proteins. Higher signals indicate regions where transcription factors can bind, essential for enhancer activity.'
        },
        'H3K27ac': {
            'label': 'Active Enhancer Mark',
            'icon': '🔵',
            'color': '#007aff',
            'description': 'Histone H3 lysine 27 acetylation marks active enhancers and promoters. Strong H3K27ac signal distinguishes active from poised enhancers, indicating current regulatory activity.'
        },
        'H3K4me1': {
            'label': 'Enhancer Mark',
            'icon': '🟢',
            'color': '#34c759',
            'description': 'Histone H3 lysine 4 mono-methylation marks both active and poised enhancers. Present at enhancers but depleted at promoters, helping distinguish enhancers from other regulatory elements.'
        },
        'H3K4me3': {
            'label': 'Promoter Mark',
            'icon': '🔴',
            'color': '#ff3b30',
            'description': 'Histone H3 lysine 4 tri-methylation marks active promoters near transcription start sites. High H3K4me3 suggests promoter rather than enhancer activity at this location.'
        },
        'RNA': {
            'label': 'RNA Expression',
            'icon': '📊',
            'color': '#5856d6',
            'description': 'RNA sequencing signal showing transcriptional activity. At enhancers, may indicate enhancer RNA (eRNA) production; in gene bodies, reflects mRNA levels.'
        }
    }
    
    @classmethod
    def generate_tabbed_charts_html(
        cls,
        mutation_id: str,
        tracks: Optional[List[str]] = None,
        show_descriptions: bool = True
    ) -> str:
        """
        Generate HTML for tabbed chart navigation.
        
        Args:
            mutation_id: Unique identifier for the mutation (used for element IDs)
            tracks: List of track IDs to display (defaults to all tracks)
            show_descriptions: Whether to show track descriptions
            
        Returns:
            HTML string for the tabbed chart component
        """
        if tracks is None:
            tracks = list(cls.TRACK_DEFINITIONS.keys())
        
        # Filter out EnhancerProbability as it's shown separately
        tracks = [t for t in tracks if t != 'EnhancerProbability']
        
        # Generate tab navigation
        tab_nav = []
        for i, track_id in enumerate(tracks):
            if track_id not in cls.TRACK_DEFINITIONS:
                continue
                
            track = cls.TRACK_DEFINITIONS[track_id]
            active_class = 'active' if i == 0 else ''
            
            tab_nav.append(f"""
                <button class="chart-tab {active_class}" 
                        onclick="switchChart('{mutation_id}', '{track_id}')"
                        data-track="{track_id}"
                        data-mutation="{mutation_id}">
                    <span class="tab-icon" style="color: {track['color']}">{track['icon']}</span>
                    <span class="tab-label">{track['label']}</span>
                </button>
            """)
        
        # Generate chart containers with descriptions
        chart_containers = []
        for i, track_id in enumerate(tracks):
            if track_id not in cls.TRACK_DEFINITIONS:
                continue
                
            track = cls.TRACK_DEFINITIONS[track_id]
            display_style = 'block' if i == 0 else 'none'
            
            description_html = ''
            if show_descriptions:
                description_html = f"""
                <div class="chart-description">
                    <p>{track['description']}</p>
                </div>
                """
            
            chart_containers.append(f"""
                <div class="chart-panel" id="panel-{mutation_id}-{track_id}" style="display: {display_style};">
                    <div class="chart-container">
                        <canvas id="chart-{mutation_id}-{track_id}"></canvas>
                    </div>
                    {description_html}
                </div>
            """)
        
        return f"""
        <div class="charts-tabbed-container">
            <div class="chart-tabs-nav">
                {''.join(tab_nav)}
            </div>
            <div class="chart-panels">
                {''.join(chart_containers)}
            </div>
        </div>
        """
    
    @classmethod
    def get_css_styles(cls) -> str:
        """
        Get CSS styles for the tabbed chart component.
        
        Returns:
            CSS string for styling the component
        """
        return """
        .charts-tabbed-container {
            margin-bottom: 32px;
            background: var(--bg-primary, #ffffff);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }
        
        .chart-tabs-nav {
            display: flex;
            gap: 0;
            background: #fafafa;
            border-bottom: 1px solid #ebebeb;
            padding: 0;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }
        
        .chart-tab {
            flex: 1;
            min-width: 140px;
            padding: 16px 20px;
            background: transparent;
            border: none;
            border-bottom: 2px solid transparent;
            cursor: pointer;
            font-family: inherit;
            font-size: 13px;
            font-weight: 500;
            color: #717171;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: all 0.2s ease;
            white-space: nowrap;
        }
        
        .chart-tab:hover {
            background: rgba(0, 0, 0, 0.02);
            color: #222222;
        }
        
        .chart-tab.active {
            color: #222222;
            background: #ffffff;
            border-bottom-color: #008489;
        }
        
        .tab-icon {
            font-size: 16px;
        }
        
        .tab-label {
            font-weight: 500;
        }
        
        .chart-panels {
            position: relative;
            background: #ffffff;
        }
        
        .chart-panel {
            padding: 0;
        }
        
        .chart-description {
            padding: 16px 24px 24px;
        }
        
        .chart-description p {
            margin: 0;
            font-size: 13px;
            line-height: 1.6;
            color: #717171;
            max-width: 800px;
            font-style: italic;
        }
        
        .chart-container {
            background: #ffffff;
            padding: 32px 24px;
            position: relative;
            height: 450px;
        }
        
        @media (max-width: 768px) {
            .tab-label {
                display: none;
            }
            .chart-tab {
                min-width: auto;
                padding: 16px;
            }
            .chart-description {
                padding: 12px 16px 16px;
            }
            .chart-container {
                padding: 20px 16px;
                height: 350px;
            }
        }
        """
    
    @classmethod
    def get_javascript_functions(cls) -> str:
        """
        Get JavaScript functions for the tabbed chart component.
        
        Returns:
            JavaScript string for component functionality
        """
        return """
        // Tab switching function for chart navigation
        function switchChart(mutationId, trackId) {
            // Get all tracks for dynamic switching (excluding EnhancerProbability which has its own section)
            const tracks = ['DNase', 'H3K27ac', 'H3K4me1', 'H3K4me3', 'RNA'];
            
            // Hide all panels for this mutation
            tracks.forEach(track => {
                const panel = document.getElementById(`panel-${mutationId}-${track}`);
                if (panel) {
                    panel.style.display = 'none';
                }
            });
            
            // Show selected panel with fade effect
            const selectedPanel = document.getElementById(`panel-${mutationId}-${trackId}`);
            if (selectedPanel) {
                selectedPanel.style.display = 'block';
                // Add smooth transition
                selectedPanel.style.opacity = '0';
                setTimeout(() => {
                    selectedPanel.style.transition = 'opacity 0.3s ease';
                    selectedPanel.style.opacity = '1';
                }, 10);
            }
            
            // Update active tab
            const tabs = document.querySelectorAll(`[data-mutation="${mutationId}"]`);
            tabs.forEach(tab => {
                tab.classList.remove('active');
                if (tab.dataset.track === trackId) {
                    tab.classList.add('active');
                }
            });
        }
        
        // Initialize first tab for each mutation on page load
        function initializeTabs() {
            const containers = document.querySelectorAll('.charts-tabbed-container');
            containers.forEach(container => {
                const firstTab = container.querySelector('.chart-tab');
                if (firstTab && !firstTab.classList.contains('active')) {
                    firstTab.click();
                }
            });
        }
        
        // Call on DOMContentLoaded if not already loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initializeTabs);
        } else {
            initializeTabs();
        }
        """
    
    @classmethod
    def get_chart_config(cls, track_id: str) -> Dict[str, Any]:
        """
        Get Chart.js configuration specific to a track type.
        
        Args:
            track_id: The track identifier
            
        Returns:
            Dictionary with Chart.js configuration options
        """
        track = cls.TRACK_DEFINITIONS.get(track_id, {})
        
        return {
            'color': track.get('color', '#000000'),
            'label': track.get('label', track_id),
            'yAxis': {
                'type': 'logarithmic' if track_id != 'RNA' else 'linear',
                'title': f"{track.get('label', track_id)} Signal"
            }
        }