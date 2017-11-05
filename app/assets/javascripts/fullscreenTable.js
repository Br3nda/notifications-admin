(function(Modules) {
  "use strict";

  Modules.FullscreenTable = function() {

    this.start = function(component) {

      this.$component = $(component);
      this.nativeHeight = this.$component.innerHeight();
      this.topOffset = this.$component.offset().top;

      this.insertShim();

      $(window).on('scroll resize', this.maintainHeight);

    };

    this.insertShim = () => this.$component.after(
      $("<div class='fullscreen-shim'/>").css({
        'height': this.nativeHeight,
        'top': this.topOffset
      })
    );

    this.maintainHeight = () => this.$component.css(
      'max-height',
      Math.min(
        $(window).height() - this.topOffset + $('html, body').scrollTop(),
        this.nativeHeight
      )
    );

  };

})(window.GOVUK.Modules);
