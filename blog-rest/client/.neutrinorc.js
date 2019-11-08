const standard = require('@neutrinojs/standardjs');
const react = require('@neutrinojs/react');

module.exports = {
  options: {
    root: __dirname,
  },
  use: [
    standard(),
    react({
      html: {
        title: 'client'
      },
      publicPath: '/blog/ui/',
      devServer: {
          port: 9052,
          historyApiFallback: {
            rewrites: [
              {
                from: /^\/blog\/ui\/.+$/,
                to: '/blog/ui/'
              }
            ]
          }
      }
    }),
  ],
};
