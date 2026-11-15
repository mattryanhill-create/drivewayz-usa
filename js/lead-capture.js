(function () {
  'use strict';

  var ENDPOINT = 'https://drivewayzusa.app.n8n.cloud/webhook/4a46a030-9b41-482a-abf5-4724062aec71';
  var THANK_YOU_URL = '/thank-you-homeowner/';
  var FORM_SELECTOR = 'form[data-lead-form="guide-sidebar"]';
  var HONEYPOT = 'hp_ref';
  var GENERIC_ERROR = 'Something went wrong. Please try again in a moment.';
  var DEFAULT_MESSAGE = 'Guide sidebar estimate request';
  var UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'];

  function injectCss() {
    if (document.getElementById('lead-capture-css')) return;
    var style = document.createElement('style');
    style.id = 'lead-capture-css';
    style.appendChild(document.createTextNode(
      FORM_SELECTOR + ' .lead-hp{position:absolute!important;left:-10000px!important;width:1px!important;height:1px!important;overflow:hidden!important;opacity:0!important;}' +
      FORM_SELECTOR + ' .lead-error{color:#ffb4a8;font-size:0.85rem;margin:0 0 0.5rem;}' +
      FORM_SELECTOR + ' .lead-error:empty{display:none;}' +
      FORM_SELECTOR + ' .lead-consent{font-size:0.75rem;line-height:1.4;color:rgba(255,255,255,0.75);margin:0.5rem 0 0;}' +
      FORM_SELECTOR + ' .lead-consent a{color:inherit;text-decoration:underline;}' +
      FORM_SELECTOR + ' [aria-invalid="true"]{border-color:#e74c3c!important;outline-color:#e74c3c;}' +
      FORM_SELECTOR + ' button[disabled]{opacity:0.7;cursor:wait;}'
    ));
    (document.head || document.getElementsByTagName('head')[0]).appendChild(style);
  }

  function field(form, name) {
    return form.querySelector('[name="' + name + '"]');
  }

  function value(form, name) {
    var el = field(form, name);
    return el && typeof el.value === 'string' ? el.value.replace(/^\s+|\s+$/g, '') : '';
  }

  function getErrorEl(form) {
    var el = form.querySelector('.lead-error');
    if (!el) {
      el = document.createElement('p');
      el.className = 'lead-error';
      el.setAttribute('role', 'alert');
      var button = form.querySelector('button[type="submit"], input[type="submit"]');
      if (button && button.parentNode) {
        button.parentNode.insertBefore(el, button);
      } else {
        form.appendChild(el);
      }
    }
    return el;
  }

  function showError(form, message) {
    getErrorEl(form).textContent = message;
  }

  function clearErrors(form) {
    var existing = form.querySelector('.lead-error');
    if (existing) existing.textContent = '';
    var invalid = form.querySelectorAll('[aria-invalid="true"]');
    for (var i = 0; i < invalid.length; i++) {
      invalid[i].removeAttribute('aria-invalid');
    }
  }

  function markInvalid(form, name) {
    var el = field(form, name);
    if (el) el.setAttribute('aria-invalid', 'true');
  }

  function safeDecode(s) {
    try {
      return decodeURIComponent(s.replace(/\+/g, ' '));
    } catch (e) {
      return s;
    }
  }

  function getQueryParam(key) {
    var query = window.location.search.replace(/^\?/, '');
    if (!query) return '';
    var pairs = query.split('&');
    for (var i = 0; i < pairs.length; i++) {
      var idx = pairs[i].indexOf('=');
      var k = idx === -1 ? pairs[i] : pairs[i].slice(0, idx);
      if (safeDecode(k) === key) {
        return idx === -1 ? '' : safeDecode(pairs[i].slice(idx + 1));
      }
    }
    return '';
  }

  function validate(form, data) {
    var errors = [];
    if (!data.name) {
      errors.push('Please enter your name.');
      markInvalid(form, 'name');
    }
    if (data.phone.replace(/\D/g, '').length < 10) {
      errors.push('Phone must contain at least 10 digits.');
      markInvalid(form, 'phone');
    }
    if (!/^\d{5}$/.test(data.zip)) {
      errors.push('ZIP code must be exactly 5 digits.');
      markInvalid(form, 'zip');
    }
    if (data.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
      errors.push('Please enter a valid email address.');
      markInvalid(form, 'email');
    }
    return errors;
  }

  function buildPayload(form, data) {
    var nameParts = data.name.split(/\s+/);
    var payload = {
      firstName: nameParts[0] || '',
      lastName: nameParts.slice(1).join(' ') || '',
      email: data.email || '',
      phone: data.phone,
      zip: data.zip,
      drivewayType: '',
      message: data.message || DEFAULT_MESSAGE,
      persona: 'homeowner',
      source: 'guide_sidebar',
      form_location: 'guide_sidebar',
      page_url: window.location.href,
      page_state: form.getAttribute('data-page-state') || ''
    };
    for (var i = 0; i < UTM_KEYS.length; i++) {
      payload[UTM_KEYS[i]] = getQueryParam(UTM_KEYS[i]);
    }
    return payload;
  }

  function redirectAfterConversion() {
    var done = false;
    function redirect() {
      if (done) return;
      done = true;
      window.location.href = THANK_YOU_URL;
    }
    if (typeof gtag === 'function') {
      setTimeout(redirect, 1000);
      try {
        gtag('event', 'generate_lead', {
          event_category: 'form',
          event_label: 'guide_sidebar',
          form_location: 'guide_sidebar',
          value: 1,
          event_callback: redirect
        });
      } catch (e) {
        redirect();
      }
    } else {
      redirect();
    }
  }

  function handleSubmit(event) {
    var form = event.currentTarget || this;
    event.preventDefault();

    if (form.getAttribute('data-lead-sending') === 'true') return;

    var button = form.querySelector('button[type="submit"], input[type="submit"]');
    var isInputButton = button && button.tagName === 'INPUT';
    var originalText = button ? (isInputButton ? button.value : button.textContent) : '';

    function setButton(disabled, text) {
      if (!button) return;
      button.disabled = disabled;
      if (isInputButton) {
        button.value = text;
      } else {
        button.textContent = text;
      }
    }

    clearErrors(form);

    // Honeypot: bots that fill every field are dropped silently.
    if (value(form, HONEYPOT)) return;

    var data = {
      name: value(form, 'name'),
      phone: value(form, 'phone'),
      zip: value(form, 'zip'),
      email: value(form, 'email'),
      message: value(form, 'message')
    };

    var errors = validate(form, data);
    if (errors.length) {
      showError(form, errors.join(' '));
      var firstInvalid = form.querySelector('[aria-invalid="true"]');
      if (firstInvalid && firstInvalid.focus) firstInvalid.focus();
      return;
    }

    function fail(err) {
      form.removeAttribute('data-lead-sending');
      setButton(false, originalText);
      showError(form, GENERIC_ERROR);
      if (window.console && console.warn) console.warn('[lead-capture]', err);
    }

    if (typeof window.fetch !== 'function') {
      fail(new Error('fetch is not supported in this browser'));
      return;
    }

    form.setAttribute('data-lead-sending', 'true');
    setButton(true, 'Sending...');

    window.fetch(ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(buildPayload(form, data))
    }).then(function (res) {
      if (res.ok) {
        redirectAfterConversion();
      } else {
        fail(new Error('HTTP ' + res.status + ' ' + (res.statusText || '')));
      }
    }, fail);
  }

  function init() {
    var forms = document.querySelectorAll(FORM_SELECTOR);
    if (!forms.length) return;
    injectCss();
    for (var i = 0; i < forms.length; i++) {
      if (forms[i].getAttribute('data-lead-bound') === 'true') continue;
      forms[i].setAttribute('data-lead-bound', 'true');
      forms[i].addEventListener('submit', handleSubmit);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
