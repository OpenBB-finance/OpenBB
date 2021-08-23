const devBuild = !(
  (process.env.NODE_ENV || "prod").trim().toLowerCase() === "prod"
);

const gulp = require("gulp");
const rename = require("gulp-rename");
const { sass } = require("@mr-hope/gulp-sass");
const cleanCSS = require("gulp-clean-css");
const autoprefixer = require("gulp-autoprefixer");
const iconfont = require("gulp-iconfont");
const filelist = require("gulp-filelist");
const uglify = require("gulp-uglify");
const sourcemaps = require("gulp-sourcemaps");
const realFavicon = require("gulp-real-favicon");
const svgSprite = require("gulp-svg-sprite");
const rev = require("gulp-rev");
const replace = require("gulp-replace");

const path = require("path");
const fs = require("fs");
const del = require("del");
const through = require("through2");

var BUILD = "build";
var CSS_BUILD = BUILD + "/assets";
var JS_BUILD = BUILD + "/assets/js";
var FONTS = "static/fonts";
var FAVICON_DATA_FILE = BUILD + "/faviconData.json";
var TIMESTAMP = Math.round(Date.now() / 1000);

function noop() {
  return through.obj();
}

gulp.task("sass", function () {
  return gulp
    .src("src/sass/{main,print,mobile}.scss")
    .pipe(devBuild ? sourcemaps.init() : noop())
    .pipe(sass().on("error", sass.logError))
    .pipe(cleanCSS({ format: "beautify" }))
    .pipe(
      autoprefixer({
        cascade: false,
      })
    )
    .pipe(gulp.dest(CSS_BUILD))
    .pipe(cleanCSS())
    .pipe(rename({ extname: ".min.css" }))
    .pipe(devBuild ? sourcemaps.write(".") : noop())
    .pipe(gulp.dest(CSS_BUILD));
});

gulp.task("favicon-generate", function (done) {
  realFavicon.generateFavicon(
    {
      masterPicture: "src/favicon/favicon-master.svg",
      dest: "static/favicon",
      iconsPath: "/favicon",
      design: {
        ios: {
          pictureAspect: "backgroundAndMargin",
          backgroundColor: "#2f333e",
          margin: "14%",
          assets: {
            ios6AndPriorIcons: false,
            ios7AndLaterIcons: false,
            precomposedIcons: false,
            declareOnlyDefaultIcon: true,
          },
        },
        desktopBrowser: {},
        windows: {
          pictureAspect: "whiteSilhouette",
          backgroundColor: "#2f333e",
          onConflict: "override",
          assets: {
            windows80Ie10Tile: false,
            windows10Ie11EdgeTiles: {
              small: false,
              medium: true,
              big: false,
              rectangle: false,
            },
          },
        },
        androidChrome: {
          pictureAspect: "shadow",
          themeColor: "#2f333e",
          manifest: {
            display: "standalone",
            orientation: "notSet",
            onConflict: "override",
            declared: true,
          },
          assets: {
            legacyIcon: false,
            lowResolutionIcons: false,
          },
        },
        safariPinnedTab: {
          pictureAspect: "silhouette",
          themeColor: "#2f333e",
        },
      },
      settings: {
        scalingAlgorithm: "Mitchell",
        errorOnImageTooSmall: false,
        readmeFile: false,
        htmlCodeFile: false,
        usePathAsIs: false,
      },
      markupFile: FAVICON_DATA_FILE,
    },
    function () {
      done();
    }
  );
});

gulp.task("favicon-check-update", function (done) {
  var currentVersion = JSON.parse(fs.readFileSync(FAVICON_DATA_FILE)).version;
  realFavicon.checkForUpdates(currentVersion, function (err) {
    if (err) {
      throw err;
    }
  });
  done();
});

gulp.task("svg-sprite", function () {
  config = {
    shape: {
      id: {
        generator: "gdoc_%s",
      },
      dimension: {
        maxWidth: 28,
        maxHeight: 28,
        attributes: false,
      },
      spacing: {
        padding: 2,
        box: "content",
      },
      dest: BUILD + "/intermediate-svg",
    },
    svg: {
      xmlDeclaration: false,
      rootAttributes: {
        class: "svg-sprite",
      },
    },
    mode: {
      inline: true,
      symbol: {
        dest: "assets/sprites/",
        sprite: "geekdoc.svg",
        bust: false,
      },
    },
  };

  return gulp
    .src("src/icons/*.svg")
    .pipe(svgSprite(config))
    .pipe(gulp.dest("."));
});

gulp.task("svg-sprite-list", function () {
  config = { removeExtensions: true, flatten: true };

  return gulp
    .src("src/icons/*.svg")
    .pipe(filelist("exampleSite/data/sprites/geekdoc.json", config))
    .pipe(gulp.dest("."));
});

gulp.task("iconfont", function () {
  var lastUnicode = 0xea01;
  var files = fs.readdirSync("src/iconfont");

  // Filter files with containing unicode value and set last unicode
  files.forEach(function (file) {
    var basename = path.basename(file);
    var matches = basename.match(/^(?:((?:u[0-9a-f]{4,6},?)+)\-)?(.+)\.svg$/i);
    var currentCode = -1;

    if (matches && matches[1]) {
      currentCode = parseInt(matches[1].split("u")[1], 16);
    }

    if (currentCode >= lastUnicode) {
      lastUnicode = ++currentCode;
    }
  });

  return gulp
    .src(["src/iconfont/*.svg"])
    .pipe(
      iconfont({
        startUnicode: lastUnicode,
        fontName: "GeekdocIcons",
        prependUnicode: true,
        normalize: true,
        fontHeight: 1001,
        centerHorizontally: true,
        formats: ["woff", "woff2"],
        timestamp: TIMESTAMP,
      })
    )
    .pipe(gulp.dest(FONTS));
});

gulp.task("js", function () {
  return gulp
    .src(["src/js/*.js"])
    .pipe(devBuild ? sourcemaps.init() : noop())
    .pipe(uglify())
    .pipe(rename({ extname: ".min.js" }))
    .pipe(devBuild ? sourcemaps.write(".") : noop())
    .pipe(gulp.dest(JS_BUILD));
});

gulp.task("asset-sync-js", function () {
  return gulp
    .src([
      "node_modules/clipboard/dist/clipboard.min.js",
      "node_modules/flexsearch/dist/flexsearch.compact.js",
      "node_modules/mermaid/dist/mermaid.min.js",
      "node_modules/katex/dist/katex.min.js",
      "node_modules/katex/dist/contrib/auto-render.min.js",
    ])
    .pipe(replace(/\/\/# sourceMappingURL=.+$/, ""))
    .pipe(
      rename(function (path) {
        path.basename = path.basename.replace(/compact/, "min");
      })
    )
    .pipe(gulp.dest(JS_BUILD));
});

gulp.task("asset-sync-css", function () {
  return gulp
    .src(["node_modules/katex/dist/katex.min.css"])
    .pipe(replace(/\/\/# sourceMappingURL=.+$/, ""))
    .pipe(
      rename(function (path) {
        path.basename = path.basename.replace(/compact/, "min");
      })
    )
    .pipe(gulp.dest(CSS_BUILD));
});

gulp.task("asset-sync-font", function () {
  return gulp
    .src(["node_modules/katex/dist/fonts/KaTeX_*"])
    .pipe(gulp.dest(FONTS));
});

gulp.task("asset-rev", function () {
  return gulp
    .src(
      [
        CSS_BUILD + "/*.min.css",
        JS_BUILD + "/*.min.js",
        JS_BUILD + "/*.compact.js",
      ],
      {
        base: BUILD + "/assets",
      }
    )
    .pipe(rev())
    .pipe(gulp.dest("static"))
    .pipe(
      rev.manifest("data/assets-static.json", {
        base: "data",
        merge: true,
      })
    )
    .pipe(rename("assets.json"))
    .pipe(gulp.dest("data"));
});

gulp.task("asset-map", function () {
  return gulp
    .src([CSS_BUILD + "/*.min.css.map", JS_BUILD + "/*.min.js.map"], {
      base: BUILD + "/assets",
    })
    .pipe(gulp.dest("static"));
});

gulp.task("clean", function () {
  return del([
    BUILD,
    "assets/sprites/",
    "static/js/",
    "static/favicon/",
    "static/*.min.css",
    "static/*.css.map",
    "data/assets.json",
    "resources",
  ]);
});

/* Task series */

gulp.task(
  "asset",
  gulp.series("asset-sync-font", "asset-sync-css", "asset-sync-js", "asset-rev")
);

gulp.task("svg", gulp.series("svg-sprite"));

gulp.task(
  "default",
  gulp.series([
    devBuild ? [] : "clean",
    "sass",
    "js",
    "asset",
    devBuild ? "asset-map" : [],
    "svg",
    "iconfont",
    "favicon-generate",
  ])
);

gulp.task("watch", function () {
  gulp.series("default")();
  gulp.watch(
    "src/sass/**/*.*css",
    gulp.series("sass", "asset-rev", "asset-map")
  );
  gulp.watch("src/js/*.js", gulp.series("js", "asset-rev", "asset-map"));
});
