(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);throw new Error("Cannot find module '"+o+"'")}var f=n[o]={exports:{}};t[o][0].call(f.exports,function(e){var n=t[o][1][e];return s(n?n:e)},f,f.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
var msgtools;

msgtools = (function($, w) {
  var removeAlert, removeConfirm, removeMsg, showAlert, showConfirm, showMsg;
  showAlert = function(content, duration) {
    if (duration == null) {
      duration = 2000;
    }
    $("#page-alert [name=content]").html(content);
    $('#page-alert').removeClass('hide');
    return setTimeout(removeAlert, duration);
  };
  removeAlert = function() {
    return $("#page-alert").addClass('hide');
  };
  showMsg = function(id, duration) {
    removeMsg();
    $('#page-posting-bg').removeClass('hide');
    $('#page-posting').removeClass('hide');
    $("#" + id).removeClass('hide');
    if (duration) {
      return setTimeout(removeMsg, duration);
    }
  };
  removeMsg = function() {
    $('#page-posting').addClass('hide');
    $('#page-posting-bg').addClass('hide');
    $('#page-posting-view').addClass('hide');
    $('#page-posting-error').addClass('hide');
    return $('#page-posting-success').addClass('hide');
  };
  showConfirm = function(content, cancel, confirm, cancel_text, confirm_text) {
    if (cancel_text == null) {
      cancel_text = '取消';
    }
    if (confirm_text == null) {
      confirm_text = '确定';
    }
    $('#page-confirm [name="content"]').html(content);
    $('#page-confirm [name="confirm-text"]').html(confirm_text);
    $('#page-confirm [name="cancel-text"]').html(cancel_text);
    $('#page-confirm').removeClass('hide');
    $('#page-backdrop').removeClass('hide');
    $('#page-confirm [name="confirm"]').on('click', (function() {
      removeConfirm();
      return typeof confirm === "function" ? confirm() : void 0;
    }));
    return $('#page-confirm [name="cancel"]').on('click', (function() {
      removeConfirm();
      return typeof cancel === "function" ? cancel() : void 0;
    }));
  };
  removeConfirm = function() {
    $('#page-confirm').addClass('hide');
    return $('#page-backdrop').addClass('hide');
  };
  return {
    makeBodyGray: function() {
      return $('body').css('background-color', '#e8edf1');
    },
    showMsg: showMsg,
    showAlert: showAlert,
    removeAlert: removeAlert,
    showConfirm: showConfirm
  };
})(Zepto, window);

module.exports = msgtools;

},{}],2:[function(require,module,exports){
var _name_, m;

_name_ = 'p';

m = require('../lib/m.js');

},{"../lib/m.js":1}]},{},[2])