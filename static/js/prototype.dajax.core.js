/* Copyright (c) 2009-2010, Benito Jorge Bastida :: For further information check COPYING */
var Dajax = Class.create();
Dajax.prototype = {
    initialize: function(){},
    process: function(data)
    {
        if(data==Dajaxice.EXCEPTION){
            alert('Something went wrong, please reload the page.');
        }
        else{
            data.each(function(elem){
            switch(elem.cmd)
            {
                case 'alert':
                    alert(elem.val)
                break;
        
                case 'data':
                    eval( elem.fun+"(elem.val);" );
                break;
        
                case 'as':
                    $$(elem.id).each(function(e){e[elem.prop] = elem.val;});
                break;
        
                case 'addcc':
                    elem.val.each(function(cssclass){
                        $$(elem.id).each(function(e){ e.addClassName(cssclass);});
                    });
                break;
        
                case 'remcc':
                    elem.val.each(function(cssclass){
                        $$(elem.id).each(function(e){ e.removeClassName(cssclass);});
                    });
                break;
        
                case 'ap':
                    $$(elem.id).each(function(e){ e[elem.prop] += elem.val;});
                break;
        
                case 'pp':
                    $$(elem.id).each(function(e){ e[elem.prop] = elem.val + e[elem.prop];});
                break;
        
                case 'clr':
                    $$(elem.id).each(function(e){e[elem.prop] = "";});
                break;
        
                case 'red':
                    window.setTimeout('window.location="'+elem.url+'";',elem.delay);
                break;
        
                case 'js':
                    eval(elem.val);
                break;
        
                case 'rm':
                    $$(elem.id).each(function(e){e.remove();});
                break;
        
                default:
                    alert('Unknown action!');
                }
            });
        }
    }
};

Dajax = new Dajax();
