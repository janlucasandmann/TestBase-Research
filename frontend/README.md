# AlphaGenome Research Platform - Frontend

A React-based web interface for exploring cancer genomics research using AlphaGenome predictions. This application provides interactive visualizations and explanations for studying how non-coding variants influence MGMT expression in glioblastoma.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The application will be available at `http://localhost:3000/`

## 📁 Project Structure

```
src/
├── components/           # React components
│   ├── Header.jsx       # Navigation header
│   ├── ResearchSection.jsx    # Research question overview
│   ├── VisualizationSection.jsx # Main visualization interface  
│   ├── VisualizationTracks.jsx  # Genomic tracks display
│   ├── ContactMap.jsx   # 3D chromatin interaction heatmap
│   └── AboutSection.jsx # AlphaGenome information
├── data/
│   └── genomicData.js   # Mock genomic data for demonstrations
├── App.jsx              # Main application component
├── main.jsx             # Application entry point
└── index.css            # Global styles
```

## 🎯 Features

### Research Question Section
- **Clear Problem Statement**: Explains the research question in accessible language
- **Key Terms Glossary**: Defines important scientific concepts
- **Research Hypotheses**: Details three main hypotheses with explanations
- **Clinical Significance**: Describes potential medical applications

### Interactive Visualizations
- **Multi-Track Genome Browser**: Shows various molecular measurements
  - Gene expression (RNA-seq)
  - Chromatin accessibility (ATAC-seq) 
  - Histone modifications (H3K27ac)
  - Transcription factor binding (ChIP-seq)
  - Splicing patterns
- **3D Contact Map**: Visualizes chromatin interactions
- **View Switching**: Compare reference vs. mutated DNA vs. differences
- **Detailed Explanations**: Each visualization includes interpretation guidance

### About AlphaGenome
- **Technical Capabilities**: Detailed explanation of AI model features
- **Cancer Applications**: Specific use cases in oncology research
- **Research Impact**: Statistics and significance
- **Future Directions**: Potential developments and applications

## 🔬 Data Integration

The current version uses mock data for demonstration purposes. In a production environment, you would:

1. **Connect to AlphaGenome API**: Replace mock data with real predictions
2. **Load Patient Data**: Import actual genomic variants from clinical datasets
3. **Real-time Analysis**: Enable on-demand variant effect predictions
4. **Data Export**: Allow users to download results and visualizations

## 🎨 Design System

The application follows a modern, scientific aesthetic:

- **Color Palette**: Blues, greens, and oranges for data visualization
- **Typography**: System fonts optimized for readability
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Accessibility**: ARIA labels and keyboard navigation support

## 🧬 Scientific Accuracy

All visualizations and explanations are based on:

- Current understanding of genome regulation
- AlphaGenome model capabilities as published by DeepMind  
- Standard genomic data visualization practices
- Clinical relevance for glioblastoma treatment

## 📊 Visualization Types

### Genomic Tracks
- **Bar Charts**: Show signal intensity across genomic positions
- **Color Coding**: Different molecular measurements have distinct colors
- **Interactive Elements**: Hover tooltips show detailed values
- **Responsive Design**: Adapts to different screen sizes

### Contact Heatmap
- **2D Matrix**: Represents 3D chromatin interaction frequencies
- **Color Gradient**: Intensity indicates interaction strength
- **Pattern Recognition**: Helps identify topological domains and loops
- **Dynamic Rendering**: Updates based on selected view mode

## 🔧 Technical Details

- **Framework**: React 19 with functional components and hooks
- **Build Tool**: Vite for fast development and optimized builds
- **Styling**: CSS modules with CSS custom properties (variables)
- **Canvas Rendering**: HTML5 Canvas for high-performance heatmap visualization
- **State Management**: React useState for local component state

## 🌐 Browser Support

- Chrome/Chromium 88+
- Firefox 85+  
- Safari 14+
- Edge 88+

## 📈 Performance

- **Bundle Size**: Optimized for fast loading
- **Canvas Rendering**: 60fps smooth animations
- **Responsive Images**: Optimized for different device pixel ratios
- **Lazy Loading**: Components load as needed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes with clear commit messages
4. Test thoroughly on different browsers and screen sizes
5. Submit a pull request with detailed description

## 📝 License

This project is part of the TestBase Research platform and follows the same MIT license terms.

---

*This frontend demonstrates how complex genomic research can be made accessible through thoughtful design and clear explanations.*