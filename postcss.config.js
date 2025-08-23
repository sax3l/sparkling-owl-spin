const path = require('path')

module.exports = {
  plugins: [
    // TailwindCSS v4 PostCSS plugin with fallback to v3
    require.resolve('@tailwindcss/postcss') || 'tailwindcss',
    
    // PostCSS Import for @import support
    require('postcss-import')({
      path: [path.join(__dirname, 'src'), path.join(__dirname, 'frontend-nextjs/src')]
    }),
    
    // Autoprefixer for vendor prefixes
    require('autoprefixer')({
      grid: 'autoplace',
      flexbox: 'no-2009'
    }),
    
    // PostCSS Nested for nested CSS support
    require('postcss-nested'),
    
    // PostCSS Custom Properties for CSS variables
    require('postcss-custom-properties')({
      preserve: false
    }),
    
    // PostCSS Color Function for color manipulation
    require('postcss-color-function'),
    
    // CSSnano for production optimization
    ...(process.env.NODE_ENV === 'production' 
      ? [
          require('cssnano')({
            preset: ['default', {
              discardComments: { removeAll: true },
              normalizeWhitespace: true,
              minifySelectors: true,
              mergeLonghand: false  // Keep compatibility with Tailwind
            }]
          })
        ] 
      : []
    )
  ],
  
  // Source maps for development
  map: process.env.NODE_ENV !== 'production' ? { inline: false } : false,
  
  // Parser options
  parser: require('postcss-scss'),
  
  // Advanced configuration for different environments
  ...(process.env.BUILD_TARGET === 'nextjs' && {
    plugins: {
      // Next.js specific PostCSS configuration
      '@tailwindcss/postcss': {},
      autoprefixer: {},
      ...(process.env.NODE_ENV === 'production' && {
        cssnano: {
          preset: 'default'
        }
      })
    }
  })
}
