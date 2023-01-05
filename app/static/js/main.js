
(function ($) {
    "use strict";

    
    /*==================================================================
    [ Validate ]*/
    var input = $('.validate-input .input100');

    $('.validate-form').on('submit',function(e){
        var check = true;

        for(var i=0; i<input.length; i++) {
            if(validate(input[i]) == false){
                showValidate(input[i]);
                check=false;
            }
        }
        if (check){
            // make ajax request
            e.preventDefault();
            let data = new FormData($("#login")[0]);
            fetch(
                new Request("/login", {
                    method : "POST",
                    body: data,
                    redirect: "follow"
                })).then( (response) => {
                    if (response.redirected) {
                        return window.location.assign(response.url);
                    }
                    response.json().then( (data) => {
                        console.log(data);
                        if (!data.authenticated) {
                            $("#msg").html("not found").css("color", "red");
                        }else {
                            return window.location.assign("/");
                        }
                        
                    }); 
            }).catch( (err) => console.error(err) );
        }

        return check;
    });


    $('.validate-form .input100').each(function(){
        $(this).focus(function(){
           $("#msg").empty(); 
           hideValidate(this);
        });
    });

    function validate (input) {
        if($(input).val().trim() == ''){
            return false;
        }
    }

    function showValidate(input) {
        var thisAlert = $(input).parent();

        $(thisAlert).addClass('alert-validate');
    }

    function hideValidate(input) {
        var thisAlert = $(input).parent();

        $(thisAlert).removeClass('alert-validate');
    }
    
    

})(jQuery);