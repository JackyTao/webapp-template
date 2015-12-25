var gulp = require('gulp');
var coffee = require('gulp-coffee');
var browserify = require('gulp-browserify');

var runSequence = require('run-sequence');
var minifycss = require('gulp-minify-css');
var plumber = require('gulp-plumber');
var jshint = require('gulp-jshint');
var uglify = require('gulp-uglify');
var stylus = require('gulp-stylus');
var jade = require('gulp-jade');
var nib = require('nib');


gulp.task('coffee', function() {
    // '/*/'匹配到的会在对应处生成相同的目录结构
    return gulp.src('ux/src/coffee/*/**/*.coffee')
        .pipe(coffee({bare: true}))
        .pipe(gulp.dest('ux/src/js/'))
});

gulp.task('jshint', function() {
    return gulp.src('ux/src/js/**/*.js')
        .pipe(jshint())
        .pipe(jshint.reporter('default'));
});

gulp.task('browserify', ['coffee'], function() {
    return gulp.src('ux/src/js/page/**/*.js')
        // 防止代码出错造成watch任务跳出
        .pipe(plumber()) 
        .pipe(browserify())
        .pipe(gulp.dest('ux/js'))
});

gulp.task('uglify', ['jshint'], function() {
    return gulp.src('ux/js/**/*.js')
        .pipe(uglify())
        .pipe(gulp.dest('webapp/static/js'));
});


gulp.task('html', function() {
    return gulp.src('ux/src/jade/*.jade')
        .pipe(plumber())
        .pipe(jade({
            pretty: true
        }))
        .pipe(gulp.dest('ux/html'))
});


gulp.task('css', function() {
    return gulp.src('ux/src/stylus/page/*.styl')
        .pipe(plumber())
        .pipe(stylus({
            use: nib(),
            import: ['nib']
        }))
        .pipe(gulp.dest('ux/css'))
        //.pipe(minifycss({compatibility:'ie7'}))
});


gulp.task('default', function() {
    runSequence('html', 'css', 'browserify');
});


gulp.task('deploy', ['default'], function() {
    gulp.src('ux/js/**/*.js')
        .pipe(gulp.dest('webapp/static/js'))

    gulp.src('ux/css/**/*')
        .pipe(gulp.dest('webapp/static/css'))
});
