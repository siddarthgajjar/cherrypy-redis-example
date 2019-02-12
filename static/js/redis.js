$(document).ready(function(){
    $("#myInput").on("keyup", function() {
        var value = $(this).val().toUpperCase();
        $.post({
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify(value),
            url: '/getData',
            error:function () {
                alert('Sorry, an error occurred. Please try again later.');
            },
            success: function(response) {
                if(response) {
                    $("#myTable").html("");
                }
                $.each(response, function(k, v) {
                        $("#myTable").append("<tr><td scope='row'>"+v['SC_CODE']+"</td><td>"+v['SC_NAME']+"</td><td>"+v['OPEN']+"</td><td>"+v['HIGH']+"</td><td>"+v['LOW']+"</td><td>"+v['CLOSE']+"</td></tr>");
                    }
                );
            }
        });
    });
});