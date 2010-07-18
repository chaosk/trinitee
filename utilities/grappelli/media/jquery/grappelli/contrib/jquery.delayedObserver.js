/*
 jQuery delayed observer - 0.8
 http://code.google.com/p/jquery-utils/

 (c) Maxime Haineault <haineault@gmail.com>
 http://haineault.com
 
 MIT License (http://www.opensource.org/licenses/mit-license.php)
 
*/

(function($){
    $.extend($.fn, {
        delayedObserver: function(callback, delay, options){
            return this.each(function(){
                var el = $(this);
                var op = options || {};
                el.data('oldval', el.val())
                    .data('condition', op.condition || function() { return ($(this).data('oldval') == $(this).val()); })
                    [(op.event||'keyup')](function(e){
                        if (el.data('condition').apply(el)) { return; }
                        else {
                            if (el.data('timer')) { clearTimeout(el.data('timer')); }
                            el.data('timer', setTimeout(function(){
                                callback.apply(el, [e]);
                            }, (delay || 0.5) * 1000));
                            el.data('oldval', el.val());
                        }
                    });
            });
        }
    });
})(jQuery);
