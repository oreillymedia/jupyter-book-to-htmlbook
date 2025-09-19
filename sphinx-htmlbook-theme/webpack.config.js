// Webpack configuration for sphinx-htmlbook-theme, derived from the sphinx-book-theme config
const { resolve } = require("path");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin"); // Compile our translation files

// Paths for various assets (sources and destinations)
const staticPath = resolve(
  __dirname,
  "src/sphinx_htmlbook_theme/theme/sphinx_htmlbook_theme/static",
);

module.exports = {
  mode: "production",
  devtool: "source-map",
  entry: {
    "sphinx-htmlbook-theme": ["./src/sphinx_htmlbook_theme/assets/scripts/index.js"],
  },
  output: {
    filename: "scripts/[name].js",
    path: staticPath,
  },
  optimization: { minimizer: ["...", new CssMinimizerPlugin()] },
  module: {
    rules: [
      {
        test: /\.scss$/,
        use: [
          { loader: MiniCssExtractPlugin.loader },
          // Interprets `@import` and `url()` like `import/require()` and will resolve them
          {
            loader: "css-loader",
            options: {
              url: false,
            },
          },
          {
            // Loads a SASS/SCSS file and compiles it to CSS
            loader: "sass-loader",
            options: {
              sassOptions: { outputStyle: "expanded" },
            },
          },
        ],
      },
    ],
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: "styles/[name].css",
    }),
  ],
};
