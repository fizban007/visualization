const webpack = require("webpack");
const path = require("path");
const resolve = require("path").resolve;
const src = resolve(__dirname, "src");
const build = resolve(__dirname, "build");
var CopyPlugin = require("copy-webpack-plugin");
// const OpenBrowserPlugin = require('open-browser-webpack-plugin');

module.exports = {
  mode: "production",

  performance: {
    hints: false
    // maxEntrypointSize: 2000000,
    // maxAssetSize: 10000000,
  },

  entry: {
    fieldlines: "./src/fieldlines.ts"
  },

  output: {
    path: path.resolve(__dirname, "app/"),
    filename: "static/[name].bundle.js"
  },

  resolve: {
    extensions: [".ts", ".tsx", ".js"]
  },

  module: {
    rules: [
      {
        test: /\.css$/,
        exclude: /node_modules/,
        use: ["style-loader", "css-loader"]
      },

      {
        test: /\.(glsl|vs|fs|vert|frag)$/,
        exclude: /node_modules/,
        use: ["raw-loader", "glslify-loader"]
      },

      {
        test: /\.tsx?$/,
        loader: "ts-loader",
        exclude: /node_modules/
      }
    ]
  },

  devServer: {
    historyApiFallback: true,
    host: "0.0.0.0",
    port: 8080,
    stats: "errors-only",
    noInfo: true,
    watchOptions: {
      aggregateTimeout: 300,
      poll: 1000,
      ignored: /node_modules/
    }
  },

  plugins: [
    new webpack.LoaderOptionsPlugin({
      minimize: true,
      debug: false,
      quiet: true
    }),

    new CopyPlugin({
      patterns: [
        {
          from: "*.html",
          to: "templates",
          context: "src/templates/"
        }
      ]
    }),
  ]
};
