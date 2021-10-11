function checkToken(obj){
    var token = localStorage.getItem('token');
    if(typeof token == "undefined" || token == null || token == ""){
        window.location.href = '/login';
    }else{
        let oReq = new XMLHttpRequest();
        oReq.open("POST", "/api/frontcheck",true);
        oReq.setRequestHeader('Authorization','Bearer ' + token);
        oReq.onreadystatechange = function (){
            if (oReq.readyState==4 && oReq.status !== 200){
                //console.log(oReq.status);
                window.location.href = '/login';
            }
        }
        oReq.send();
        /*
      obj.ajax({
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
      }) */
    }
}
checkToken();
