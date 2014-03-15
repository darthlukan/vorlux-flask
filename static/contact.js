$(document).tooltip();

$("#send").button();

$(document).ready(function() {
    // Contact form:
    //noinspection JSUnusedGlobalSymbols
    $('#contact-form').validate({
        submitHandler: function(form) {
            $('#contact-form').submit(function() {

                $.ajax({
                    type : 'POST',
                    url : "/test/php/contact.php",
                    data : $('#contact-form').serialize(), //Thanks Tim Withers! http://stackoverflow.com/a/12136157/1016320
                    success : function() {
                        alert("Email Sent! Thank you for your feedback.");
                        $('#contact-form').each(function() {
                            this.reset();
                        });
                    }
                });
                // If we don't return false, we'll use the
                // old HTML way which is exactly what we don't want.
                return false;
            });
        }
    });
});

