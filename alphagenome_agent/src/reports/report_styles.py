"""
Reusable CSS styles module for HTML reports.

This module contains all CSS styles used across different report generators
to maintain consistency and enable easy reuse.
"""

from typing import Dict, Any, List


class ReportStyles:
    """Centralized CSS styles for HTML reports."""
    
    @staticmethod
    def get_base_styles() -> str:
        """Get base CSS styles for all reports."""
        return """
        <style>
        /* Base Variables */
        :root {
            --primary-color: #0066cc;
            --accent-blue: #007bff;
            --accent-green: #00a699;
            --bg-primary: #ffffff;
            --bg-secondary: #f8f9fa;
            --bg-tertiary: #e9ecef;
            --text-primary: #2c3e50;
            --text-secondary: #495057;
            --text-muted: #6c757d;
            --border-light: #dee2e6;
            --shadow-card: 0 2px 4px rgba(0, 0, 0, 0.1);
            --shadow-hover: 0 4px 8px rgba(0, 0, 0, 0.15);
        }

        /* Base Layout */
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.6;
            color: var(--text-primary);
            background: #f8f9fa;
            margin: 0;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: var(--shadow-card);
            overflow: hidden;
        }

        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            line-height: 1.3;
            margin-top: 0;
        }

        h1 {
            font-size: 2.5rem;
            color: var(--primary-color);
            margin-bottom: 0.5rem;
        }

        h2 {
            font-size: 1.8rem;
            color: var(--text-primary);
            margin-bottom: 1rem;
            border-bottom: 2px solid var(--accent-blue);
            padding-bottom: 0.5rem;
        }

        h3 {
            font-size: 1.4rem;
            color: var(--text-primary);
            margin-bottom: 1rem;
        }

        /* Sections */
        .section {
            padding: 24px;
            margin-bottom: 24px;
            border-radius: 8px;
            background: var(--bg-primary);
            box-shadow: var(--shadow-card);
        }

        .section-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
        }

        .section-description {
            color: var(--text-secondary);
            font-size: 14px;
            margin-bottom: 20px;
            line-height: 1.6;
        }

        /* Cards */
        .card {
            background: var(--bg-primary);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: var(--shadow-card);
            transition: box-shadow 0.2s ease;
        }

        .card:hover {
            box-shadow: var(--shadow-hover);
        }

        /* Badges */
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }

        .badge.success {
            background: #d4edda;
            color: #155724;
        }

        .badge.warning {
            background: #fff3cd;
            color: #856404;
        }

        .badge.danger {
            background: #f8d7da;
            color: #721c24;
        }

        .badge.info {
            background: #d1ecf1;
            color: #0c5460;
        }

        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 16px 0;
            font-size: 14px;
            background: var(--bg-primary);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: var(--shadow-card);
        }

        th, td {
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid var(--border-light);
        }

        th {
            background: var(--bg-tertiary);
            font-weight: 600;
            color: var(--text-secondary);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        tr:hover {
            background: rgba(0, 102, 204, 0.02);
        }

        tr:last-child td {
            border-bottom: none;
        }

        /* Buttons */
        .btn {
            display: inline-block;
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            text-decoration: none;
            transition: all 0.2s ease;
        }

        .btn-primary {
            background: var(--primary-color);
            color: white;
        }

        .btn-primary:hover {
            background: #0056b3;
        }

        .btn-secondary {
            background: var(--bg-tertiary);
            color: var(--text-secondary);
        }

        .btn-secondary:hover {
            background: #dee2e6;
        }

        /* Charts */
        .chart-container {
            position: relative;
            height: 400px;
            margin: 20px 0;
            background: var(--bg-primary);
            border-radius: 8px;
            padding: 20px;
            box-shadow: var(--shadow-card);
        }

        /* Utility Classes */
        .text-center {
            text-align: center;
        }

        .text-right {
            text-align: right;
        }

        .mb-0 { margin-bottom: 0; }
        .mb-1 { margin-bottom: 0.5rem; }
        .mb-2 { margin-bottom: 1rem; }
        .mb-3 { margin-bottom: 1.5rem; }
        .mb-4 { margin-bottom: 2rem; }

        .mt-0 { margin-top: 0; }
        .mt-1 { margin-top: 0.5rem; }
        .mt-2 { margin-top: 1rem; }
        .mt-3 { margin-top: 1.5rem; }
        .mt-4 { margin-top: 2rem; }

        /* Responsive */
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
            
            .container {
                border-radius: 0;
            }
            
            h1 {
                font-size: 2rem;
            }
            
            .section {
                padding: 16px;
            }
        }
        </style>
        """
    
    @staticmethod
    def get_decision_panel_styles() -> str:
        """Get styles for decision panels."""
        return """
        <style>
        .decision-panel {
            background: white;
            border: 2px solid #28a745;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .decision-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .decision-badge.not-applicable {
            background: #6c757d;
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .decision-box {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
        }
        
        .decision-note {
            color: #28a745;
            font-style: italic;
            margin-top: 10px;
        }
        
        .not-evaluated-badge {
            background: #ffc107;
            color: #212529;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            margin-left: 8px;
        }
        </style>
        """
    
    @staticmethod
    def get_chart_styles() -> str:
        """Get styles for charts and visualizations."""
        return """
        <style>
        .probability-chart-section,
        .signal-profile-section {
            margin: 24px 0;
            padding: 24px;
            background: var(--bg-primary);
            border-radius: 8px;
            box-shadow: var(--shadow-card);
        }
        
        .probability-chart-container,
        .signal-chart-container {
            position: relative;
            height: 400px;
            margin: 20px 0;
            background: var(--bg-primary);
            border-radius: 6px;
        }
        
        .probability-explanation,
        .signal-explanation {
            margin-top: 20px;
        }
        
        .explanation-toggle {
            background: var(--bg-secondary);
            border: 1px solid var(--border-light);
            border-radius: 6px;
            padding: 12px 16px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            color: var(--text-secondary);
            width: 100%;
            text-align: left;
            transition: all 0.2s ease;
        }
        
        .explanation-toggle:hover {
            background: var(--bg-tertiary);
            color: var(--text-primary);
        }
        
        .explanation-content {
            background: var(--bg-secondary);
            border-radius: 6px;
            padding: 20px;
            margin-top: 12px;
            border-left: 4px solid var(--accent-blue);
        }
        
        .explanation-section {
            margin-bottom: 24px;
        }
        
        .explanation-section:last-child {
            margin-bottom: 0;
        }
        
        .signal-list {
            display: grid;
            gap: 12px;
            margin: 16px 0;
        }
        
        .signal-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 8px 0;
        }
        
        .signal-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            min-width: 80px;
            text-align: center;
        }
        
        .signal-badge.positive {
            background: rgba(0, 166, 153, 0.1);
            color: var(--accent-green);
        }
        
        .signal-badge.negative {
            background: rgba(220, 53, 69, 0.1);
            color: #dc3545;
        }
        
        .signal-badge.neutral {
            background: rgba(108, 117, 125, 0.1);
            color: var(--text-muted);
        }
        
        .signal-desc {
            color: var(--text-secondary);
            font-size: 13px;
            line-height: 1.4;
        }
        
        .method-note,
        .limitation-note {
            background: var(--bg-tertiary);
            padding: 12px;
            border-radius: 4px;
            font-size: 13px;
            color: var(--text-secondary);
            margin-top: 16px;
        }
        
        .limitation-box ul {
            margin: 8px 0 0 0;
            padding-left: 20px;
        }
        
        .limitation-box li {
            margin-bottom: 6px;
            font-size: 13px;
        }
        
        .toggle-icon {
            float: right;
            transition: transform 0.2s ease;
        }
        
        .toggle-icon.rotated {
            transform: rotate(180deg);
        }
        </style>
        """
    
    @staticmethod
    def get_evidence_styles() -> str:
        """Get styles for evidence display."""
        return """
        <style>
        .evidence-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin: 20px 0;
        }
        
        .evidence-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            background: var(--bg-primary);
            border-radius: 8px;
            font-size: 14px;
            box-shadow: var(--shadow-card);
        }
        
        .evidence-icon {
            width: 32px;
            height: 32px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            flex-shrink: 0;
        }
        
        .evidence-positive {
            background: rgba(0, 166, 153, 0.1);
            color: var(--accent-green);
        }
        
        .evidence-negative {
            background: rgba(113, 113, 113, 0.1);
            color: var(--text-secondary);
        }
        
        .criteria-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin: 24px 0;
            font-size: 14px;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid var(--border-light);
        }
        
        .criteria-table th {
            background: #f7f7f7;
            padding: 16px;
            text-align: left;
            font-weight: 600;
            color: var(--text-secondary);
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid var(--border-light);
        }
        
        .criteria-table td {
            padding: 16px;
            border-bottom: 1px solid var(--border-light);
            color: var(--text-primary);
            background: var(--bg-primary);
        }
        
        .criteria-pass {
            color: #28a745;
            font-weight: 600;
        }
        
        .criteria-fail {
            color: #dc3545;
            font-weight: 600;
        }
        
        .score-bar {
            width: 100%;
            height: 20px;
            background: var(--bg-tertiary);
            border-radius: 10px;
            overflow: hidden;
            margin-top: 8px;
        }
        
        .score-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--accent-green), var(--accent-blue));
            border-radius: 10px;
            transition: width 0.8s ease;
        }
        </style>
        """
    
    @staticmethod
    def get_genome_browser_styles() -> str:
        """Get styles for genome browser visualization."""
        return """
        <style>
        .genome-browser-section {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }
        
        .browser-panel {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin-top: 16px;
        }
        
        .browser-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #dee2e6;
        }
        
        .browser-position {
            font-family: 'Courier New', monospace;
            font-size: 16px;
            font-weight: 600;
            color: #2c3e50;
        }
        
        .browser-link {
            color: #007bff;
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
        }
        
        .browser-link:hover {
            text-decoration: underline;
        }
        
        .tracks-container {
            margin: 20px 0;
        }
        
        .track-row {
            display: flex;
            align-items: center;
            margin-bottom: 12px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 6px;
        }
        
        .track-label {
            width: 100px;
            font-size: 13px;
            font-weight: 600;
            color: #495057;
        }
        
        .track-visualization {
            flex: 1;
            height: 35px;
            position: relative;
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            overflow: hidden;
            margin: 0 10px;
        }
        
        .track-bar {
            position: absolute;
            bottom: 0;
            height: 100%;
            transition: all 0.3s ease;
        }
        
        .track-bar-ref {
            background: linear-gradient(to top, rgba(0, 102, 204, 0.8), rgba(0, 102, 204, 0.3));
            left: 0;
        }
        
        .track-bar-alt {
            background: linear-gradient(to top, rgba(255, 149, 0, 0.8), rgba(255, 149, 0, 0.3));
            right: 0;
        }
        
        .track-value {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            font-size: 10px;
            font-weight: 600;
            color: white;
            padding: 2px 4px;
            border-radius: 3px;
            background: rgba(0,0,0,0.6);
        }
        
        .browser-legend {
            display: flex;
            gap: 20px;
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid #dee2e6;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            color: #495057;
        }
        
        .legend-color {
            width: 16px;
            height: 16px;
            border-radius: 3px;
        }
        
        .legend-line {
            width: 20px;
            height: 2px;
            border-top: 2px solid;
        }
        
        .track-interpretation {
            margin-top: 20px;
            padding: 15px;
            background: #e9ecef;
            border-radius: 6px;
        }
        
        .track-interpretation h4 {
            font-size: 14px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .track-interpretation ul {
            margin: 0;
            padding-left: 20px;
        }
        
        .track-interpretation li {
            font-size: 12px;
            color: #495057;
            line-height: 1.6;
            margin-bottom: 6px;
        }
        </style>
        """
    
    @staticmethod
    def get_delta_analysis_styles() -> str:
        """Get styles for delta analysis visualization."""
        return """
        <style>
        .delta-analysis-section {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }
        
        .delta-panel {
            background: white;
            padding: 20px;
            border-radius: 6px;
            margin-top: 15px;
        }
        
        .delta-grid {
            display: grid;
            gap: 20px;
            margin: 20px 0;
        }
        
        .delta-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
        }
        
        .delta-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        
        .delta-label {
            font-weight: 600;
            color: #2c3e50;
        }
        
        .delta-percentile {
            font-size: 12px;
            color: #6c757d;
        }
        
        .delta-bar-container {
            background: #e9ecef;
            height: 30px;
            border-radius: 4px;
            position: relative;
        }
        
        .delta-bar {
            height: 100%;
            border-radius: 4px;
            display: flex;
            align-items: center;
            padding: 0 10px;
            transition: width 0.3s ease;
        }
        
        .delta-bar.gain {
            background: linear-gradient(to right, #28a745, #20c997);
        }
        
        .delta-bar.loss {
            background: linear-gradient(to right, #dc3545, #fd7e14);
        }
        
        .delta-value {
            color: white;
            font-weight: 600;
            font-size: 12px;
        }
        
        .novelty-interpretation {
            margin-top: 20px;
            padding: 15px;
            background: #e9ecef;
            border-radius: 6px;
        }
        
        .novelty-interpretation h4 {
            font-size: 14px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .novelty-interpretation p {
            margin: 0;
            color: #495057;
            font-size: 13px;
        }
        </style>
        """
    
    @staticmethod
    def get_hgvs_styles() -> str:
        """Get styles for HGVS notation section."""
        return """
        <style>
        .hgvs-notation-section {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }
        
        .hgvs-panel {
            background: white;
            border-radius: 6px;
            padding: 20px;
            margin-top: 15px;
        }
        
        .hgvs-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 25px;
        }
        
        .hgvs-table th {
            background: #e9ecef;
            padding: 10px;
            text-align: left;
            font-size: 12px;
            font-weight: 600;
            color: #495057;
            border-bottom: 2px solid #dee2e6;
        }
        
        .hgvs-table td {
            padding: 10px;
            border-bottom: 1px solid #dee2e6;
            font-size: 13px;
            color: #495057;
        }
        
        .mono-font {
            font-family: 'Courier New', monospace;
            font-weight: 600;
            color: #2c3e50;
        }
        
        .protein-effect {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
        }
        
        .protein-effect h4 {
            font-size: 14px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 15px;
        }
        
        .effect-details {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-bottom: 15px;
        }
        
        .effect-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .effect-label {
            font-size: 12px;
            font-weight: 600;
            color: #6c757d;
            min-width: 100px;
        }
        
        .effect-value {
            font-size: 13px;
            color: #2c3e50;
            font-weight: 500;
        }
        
        .effect-value.high-impact {
            color: #dc3545;
            font-weight: 600;
        }
        
        .effect-value.moderate-impact {
            color: #ffc107;
            font-weight: 600;
        }
        
        .effect-value.low-impact {
            color: #28a745;
            font-weight: 600;
        }
        
        .impact-description {
            background: #e9ecef;
            padding: 12px;
            border-radius: 4px;
            margin-top: 15px;
        }
        
        .impact-description p {
            margin: 0;
            font-size: 12px;
            color: #495057;
            line-height: 1.6;
        }
        </style>
        """
    
    @staticmethod
    def get_provenance_styles() -> str:
        """Get styles for data provenance section."""
        return """
        <style>
        .data-provenance-section {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }
        
        .data-provenance-section h3 {
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 18px;
        }
        
        .provenance-table {
            overflow-x: auto;
            margin-bottom: 20px;
        }
        
        .provenance-table table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 4px;
            overflow: hidden;
        }
        
        .provenance-table th {
            background: #e9ecef;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #495057;
            border-bottom: 2px solid #dee2e6;
        }
        
        .provenance-table td {
            padding: 10px 12px;
            border-bottom: 1px solid #dee2e6;
            color: #495057;
        }
        
        .provenance-table tr:last-child td {
            border-bottom: none;
        }
        
        .reproducibility-note {
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 4px;
            padding: 15px;
            margin-top: 20px;
        }
        
        .reproducibility-note h4 {
            color: #856404;
            margin-bottom: 10px;
            font-size: 14px;
        }
        
        .reproducibility-note ul {
            margin: 0;
            padding-left: 20px;
            color: #856404;
        }
        
        .reproducibility-note li {
            margin-bottom: 8px;
            font-size: 13px;
            line-height: 1.5;
        }
        </style>
        """
    
    @staticmethod
    def get_all_styles() -> str:
        """Get all styles combined for complete reports."""
        return (
            ReportStyles.get_base_styles() +
            ReportStyles.get_decision_panel_styles() +
            ReportStyles.get_chart_styles() +
            ReportStyles.get_evidence_styles() +
            ReportStyles.get_genome_browser_styles() +
            ReportStyles.get_delta_analysis_styles() +
            ReportStyles.get_hgvs_styles() +
            ReportStyles.get_provenance_styles()
        )
    
    @staticmethod
    def get_custom_styles(sections: List[str]) -> str:
        """Get specific style sections."""
        style_methods = {
            'base': ReportStyles.get_base_styles,
            'decision': ReportStyles.get_decision_panel_styles,
            'charts': ReportStyles.get_chart_styles,
            'evidence': ReportStyles.get_evidence_styles,
            'browser': ReportStyles.get_genome_browser_styles,
            'delta': ReportStyles.get_delta_analysis_styles,
            'hgvs': ReportStyles.get_hgvs_styles,
            'provenance': ReportStyles.get_provenance_styles,
        }
        
        combined_styles = ""
        for section in sections:
            if section in style_methods:
                combined_styles += style_methods[section]()
        
        return combined_styles