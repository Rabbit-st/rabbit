function checkToken(){
    var token = localStorage.getItem('token');
    if(typeof token == "undefined" || token == null || token == ""){
        window.location.href = '/login';
    }else{
      $.ajax({
        url: '/api/frontcheck',
        type: 'post',
        dataType: 'json',
        headers: {
            "Authorization": 'Bearer ' + token
        },
        error:function(data){
            if (data.status != 200 ){
                window.location.href = '/login';
            }
        }
      })
    }
}
checkToken()
