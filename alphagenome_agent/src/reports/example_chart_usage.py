"""
Example demonstrating how to use the TabbedChartComponent in other reports.

This shows how the modular chart component can be easily integrated
into different types of genomic analysis reports.
"""

from chart_components import TabbedChartComponent


def create_example_report():
    """Example of using the tabbed chart component in a custom report."""
    
    # Example 1: Use all default tracks with descriptions
    charts_html_full = TabbedChartComponent.generate_tabbed_charts_html(
        mutation_id="example-mutation-1",
        show_descriptions=True
    )
    
    # Example 2: Use only specific tracks
    charts_html_subset = TabbedChartComponent.generate_tabbed_charts_html(
        mutation_id="example-mutation-2", 
        tracks=['DNase', 'H3K27ac', 'H3K4me1'],
        show_descriptions=True
    )
    
    # Example 3: Without descriptions for compact view
    charts_html_compact = TabbedChartComponent.generate_tabbed_charts_html(
        mutation_id="example-mutation-3",
        show_descriptions=False
    )
    
    # Get the CSS styles (include once in <head>)
    css_styles = TabbedChartComponent.get_css_styles()
    
    # Get the JavaScript functions (include once before </body>)
    js_functions = TabbedChartComponent.get_javascript_functions()
    
    # Create full HTML report
    html_report = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Example Report with Tabbed Charts</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            {css_styles}
            
            /* Additional custom styles */
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                margin: 40px;
                background: #fafafa;
            }}
            
            .report-section {{
                background: white;
                padding: 30px;
                margin-bottom: 30px;
                border-radius: 12px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }}
            
            h2 {{
                color: #222;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="report-section">
            <h2>Full Track Display with Descriptions</h2>
            {charts_html_full}
        </div>
        
        <div class="report-section">
            <h2>Subset of Tracks (Enhancer-focused)</h2>
            {charts_html_subset}
        </div>
        
        <div class="report-section">
            <h2>Compact View (No Descriptions)</h2>
            {charts_html_compact}
        </div>
        
        <script>
            // Your Chart.js initialization code here
            // ...
            
            // Include the tab switching functions
            {js_functions}
        </script>
    </body>
    </html>
    """
    
    return html_report


def integrate_with_existing_report(mutation_results):
    """
    Example of integrating the chart component into an existing report generator.
    
    Args:
        mutation_results: List of mutation analysis results
    """
    
    html_sections = []
    
    for result in mutation_results:
        mutation_id = result.get('id', 'unknown')
        
        # Generate charts for this mutation
        charts_html = TabbedChartComponent.generate_tabbed_charts_html(
            mutation_id=mutation_id,
            tracks=['DNase', 'H3K27ac', 'H3K4me1', 'H3K4me3', 'RNA'],
            show_descriptions=True
        )
        
        # Add to your report structure
        section = f"""
        <div class="mutation-result">
            <h3>Mutation: {mutation_id}</h3>
            {charts_html}
            <!-- Additional analysis results here -->
        </div>
        """
        
        html_sections.append(section)
    
    return '\n'.join(html_sections)


def get_track_info():
    """
    Example showing how to access track metadata for custom displays.
    """
    
    # Access track definitions for custom UI
    for track_id, track_info in TabbedChartComponent.TRACK_DEFINITIONS.items():
        print(f"Track: {track_id}")
        print(f"  Label: {track_info['label']}")
        print(f"  Icon: {track_info['icon']}")
        print(f"  Color: {track_info['color']}")
        print(f"  Description: {track_info['description']}")
        print()


if __name__ == "__main__":
    # Generate example report
    report = create_example_report()
    
    # Save to file
    with open("example_tabbed_chart_report.html", "w") as f:
        f.write(report)
    
    print("Example report generated: example_tabbed_chart_report.html")
    
    # Show track information
    print("\nAvailable tracks:")
    get_track_info()