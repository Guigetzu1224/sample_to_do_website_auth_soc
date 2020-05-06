$(document).ready(function() { 
$(function(){
  $("#menu").on("click" , function(){
    $(this).toggleClass("active");
    $("body").toggleClass("nav-open");
  });

  $(function()
{
	$("#datepicker" ).datepicker();
});
$(function()
{
	$("#datepicker2" ).datepicker();
});
});

var password = document.getElementById("password")
  , confirm_password = document.getElementById("confirm_password");

function validatePassword(){
  if(password.value != confirm_password.value) {
    confirm_password.setCustomValidity("Passwords Don't Match");
  } else {
    confirm_password.setCustomValidity('');
  }
}

password.onchange = validatePassword;
confirm_password.onkeyup = validatePassword;


});