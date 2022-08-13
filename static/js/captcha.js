function getElementAbsPos(e)
{
    var t = e.offsetTop;
    var l = e.offsetLeft;
    while(e = e.offsetParent)
    {
        t += e.offsetTop;
	l += e.offsetLeft;
    }

    return {left:l,top:t};
}

function choose(){
    var eve = window.event;
    captcha_img = document.getElementById("captcha_img");
    captcha_div = document.getElementById("captcha_div");
    captcha_img_pos = getElementAbsPos(captcha_img);
    captcha_div_pos = getElementAbsPos(captcha_div);
    clicked_count = document.getElementById("clicked").innerHTML;
    total_count = document.getElementById("total").innerHTML;

    if (parseInt(clicked_count) < parseInt(total_count)){
        number_img = document.getElementById("captcha-number-"+(parseInt(clicked_count)+1));
        number_img.style = "position: absolute; top: "+(eve.pageY-captcha_div_pos["top"]-15)+"px; left: "+(eve.pageX-captcha_div_pos["left"]-15)+"px";
        document.getElementById("clicked").innerHTML = parseInt(clicked_count)+1;
        clicked_pos = document.getElementById("clicked_pos").innerHTML;
        clicked_pos = clicked_pos + (eve.pageX-captcha_img_pos["left"]) + "," + (eve.pageY-captcha_img_pos["top"]) + ",";
        document.getElementById("clicked_pos").innerHTML = clicked_pos;
    }

}

function clear_all(){
    numbers = document.getElementsByClassName("captcha-numbers");
    for (var i=0;i<numbers.length;i++){
        numbers[i].style = "display: none";
    }
    document.getElementById("clicked_pos").innerHTML = "";
    document.getElementById("clicked").innerHTML = "0";
}

function submit_captcha(){
    document.getElementById("submit_button").innerHTML = "...";
    var httpRequest =new XMLHttpRequest();
    httpRequest.open('POST','/api/get_token',true);
    httpRequest.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    httpRequest.send("id="+document.getElementById("captcha-id").innerHTML+"&pos="+document.getElementById("clicked_pos").innerHTML);
    httpRequest.onreadystatechange =function () {
        if (httpRequest.readyState == 4) {
            var text = httpRequest.responseText;
            var json = JSON.parse(text);
            if (json.validity === true){
                document.getElementById("captcha-token").value = json.token;
                document.getElementById("submit_button").innerHTML = "确定";
                document.getElementById("captcha-window").style = "display: none";
            }
            else{
                document.getElementById("submit_button").innerHTML = "确定";
                document.getElementById("captcha_result").innerHTML = json.message;
                get_captcha_img();
            }
        }
    }
}

function get_captcha_img(){
    document.getElementById("loading-tips").style = "position: absolute; top: 50px; left: 0px";
    document.getElementById("captcha_img").style = "display:none";
    clear_all();
    var httpRequest = new XMLHttpRequest();
    httpRequest.open('POST','/api/get_image',true);
    httpRequest.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    httpRequest.send('');

    httpRequest.onreadystatechange =function () {
        if (httpRequest.readyState === 4) {
            var text = httpRequest.responseText;
            var json = JSON.parse(text);
            document.getElementById("captcha_img").src = json.captcha_img;
            document.getElementById("captcha-id").innerHTML = json.captcha_id;
            document.getElementById("total").innerHTML = json.captcha_lens;
            document.getElementById("loading-tips").style = "display:none";
            document.getElementById("captcha_img").style = "position: absolute; top: 50px; left: 0px";
            document.getElementById("captcha_result").innerHTML = "";
        }
    }
}

