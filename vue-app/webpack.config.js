const path = require("path")
const VueLoaderPlugin = require("vue-loader/lib/plugin")
require("dotenv").config()

module.exports = {
	entry: ["@babel/polyfill", "./src/app.js"],
	output: {
		path: path.resolve(__dirname, "server/static/dist"),
		filename: "bundle.js"
	},
	resolve: {
		alias: {
			vue$: "vue/dist/vue.common.js"
		}
	},
	module: {
		rules: [
			{
				test: /\.js$/,
				exclude: /node_modules/,
				use: [
					{
						loader: "babel-loader",
						options: {
							presets: [
								"@babel/preset-env"
							]
						}
					}
				]
			},
			{
				test: /\.vue$/,
				use: "vue-loader"
			},
			{
				test: /\.(scss|css)$/,
				use: [
					"style-loader",
					"css-loader",
					"sass-loader"
				]
			}
		]
	},
	plugins: [
		new VueLoaderPlugin()
	],
	devServer: {
		contentBase: [
			path.join(__dirname, "server"),
			path.join(__dirname, "server", "templates"),
		],
		proxy: {
			"/api": {
				target: process.env.DEV_SERVER_PROXY_TO
			}
		}
	}
}