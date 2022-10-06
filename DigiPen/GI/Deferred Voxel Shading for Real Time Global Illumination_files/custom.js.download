jQuery(document).ready(function($){
    //function to check if the .cd-image-container is in the viewport here
    // ...
     
    //make the .cd-handle element draggable and modify .cd-resize-img width according to its position
    $('.cd-image-container').each(function(){
       var actual = $(this);
       drags(actual.find('.cd-handle'), actual.find('.cd-resize-img'), actual);
    });
 
    //function to upadate images label visibility here
    // ...
 });
 
 //draggable funtionality - credits to http://css-tricks.com/snippets/jquery/draggable-without-jquery-ui/
 function drags(dragElement, resizeElement, container) {
    dragElement.on("mousedown vmousedown", function(e) {
       dragElement.addClass('draggable');
       resizeElement.addClass('resizable');
 
       var dragWidth = dragElement.outerWidth(),
           xPosition = dragElement.offset().left + dragWidth - e.pageX,
           containerOffset = container.offset().left,
           containerWidth = container.outerWidth(),
           minLeft = containerOffset + 10,
           maxLeft = containerOffset + containerWidth - dragWidth - 10;
         
       dragElement.parents().on("mousemove vmousemove", function(e) {
          leftValue = e.pageX + xPosition - dragWidth;
             
          //constrain the draggable element to move inside its container
          if(leftValue < minLeft ) {
             leftValue = minLeft;
          } else if ( leftValue > maxLeft) {
             leftValue = maxLeft;
          }
 
          widthValue = (leftValue + dragWidth/2 - containerOffset)*100/containerWidth+'%';
 
          $('.draggable').css('left', widthValue).on("mouseup vmouseup", function() {
             $(this).removeClass('draggable');
             resizeElement.removeClass('resizable');
          });
 
          $('.resizable').css('width', widthValue); 
 
          //function to upadate images label visibility here
          // ...
 
       }).on("mouseup vmouseup", function(e){
          dragElement.removeClass('draggable');
          resizeElement.removeClass('resizable');
       });
       e.preventDefault();
    }).on("mouseup vmouseup", function(e) {
       dragElement.removeClass('draggable');
       resizeElement.removeClass('resizable');
    });
 }


// Select all links with hashes
$('a[href*="#"]')
    // Remove links that don't actually link to anything
    .not('[href="#"]')
    .not('[href="#0"]')
    .click(function (event) {
        // On-page links
        if (
            location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') &&
            location.hostname == this.hostname
        ) {
            // Figure out element to scroll to
            var target = $(this.hash);
            target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
            // Does a scroll target exist?
            if (target.length) {
                // Only prevent default if animation is actually gonna happen
                event.preventDefault();
                $('html, body').animate({
                    scrollTop: target.offset().top
                }, 1000, function () {
                    // Callback after animation
                    // Must change focus!
                    var $target = $(target);
                    $target.focus();
                    if ($target.is(":focus")) { // Checking if the target was focused
                        return false;
                    } else {
                        $target.attr('tabindex', '-1'); // Adding tabindex for elements not focusable
                        $target.focus(); // Set focus again
                    };
                });
            }
        }
    });