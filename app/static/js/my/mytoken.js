function savelStorage(key, value){
    if (window.localStorage) {
        var storage=window.localStorage;
        storage.setItem(key, value);
        return true;
    }else{
        return false;
    }
}
function savelStorageJson(data){
    if (window.localStorage) {
        var storage=window.localStorage;
        var d=JSON.stringify(data);
        storage.setItem("data", d);
        return true;
    }else{
        return false;
    }
}
function getToken(){
    if (window.localStorage) {
        var storage=window.localStorage;
        var token=storage.getItem("token");
        if(typeof token == "undefined" || token == null || token == ""){
            return false;
        }else{
            return token;
        }
    }
}
function getlStorage(key){
  if (window.localStorage) {
    var name=window.localStorage.getItem(key);
    if(typeof name == "undefined" || name == null || name == ""){
      return false;
    }else{
      return name;
    }
  }
}
