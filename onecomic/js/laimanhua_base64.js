//获取当前图片
function getUrlpics(){
       var PicUrls=picTree;
     
       if (PicUrls.indexOf("mh160tuku")==-1)
       PicUrls=base64_decode(picTree); 
       
       if(PicUrls.indexOf("JLmh160")!=-1)
       {PicUrls=ithmsh(PicUrls);}
       else if(PicUrls.indexOf("TWmh160")!=-1){
       PicUrls=itwrnm(PicUrls);}
       var PicUrlArr=PicUrls.split("$qingtiandy$");
       return PicUrlArr

}

//获取当前图片

function getrealurl(urlstr){
       var realurl=urlstr;
    
       if(realurl.indexOf("img1.fshmy.com")!=-1){
    
          realurl=realurl.replace("img1.fshmy.com","img1.hgysxz.cn");
       }
       else if(realurl.indexOf("imgs.k6188.com")!=-1){
         
           realurl=realurl.replace("imgs.k6188.com","imgs.zhujios.com");                      
  }
      else if(realurl.indexOf("073.k6188.com")!=-1){
         
           realurl=realurl.replace("073.k6188.com","cartoon.zhujios.com");                      
  }
      else if(realurl.indexOf("cartoon.jide123.cc")!=-1){
         
           realurl=realurl.replace("cartoon.jide123.cc","cartoon.shhh88.com");                      
  }
      else if(realurl.indexOf("imgs.gengxin123.com")!=-1){
         
           realurl=realurl.replace("imgs.gengxin123.com","imgs1.ysryd.com");                      
  }
      else if(realurl.indexOf("www.jide123.com")!=-1){
         
           realurl=realurl.replace("www.jide123.com","cartoon.shhh88.com");                      
       }   
      else if(realurl.indexOf("cartoon.chuixue123.com")!=-1){
         
           realurl=realurl.replace("cartoon.chuixue123.com","cartoon.shhh88.com");                      
       }
      else if(realurl.indexOf("p10.tuku.cc:8899")!=-1){
         
           realurl=realurl.replace("p10.tuku.cc:8899","tkpic.tukucc.com");                      
       }
      else if(realurl.indexOf("http://")==-1){
         
         
           realurl=encodeURI(getpicdamin() + realurl); 
   
          //realurl=getpicdamin()+"/url.asp?url=" + realurl;

          
          //if (realurl.indexOf("mhpic5")!=-1)
          //realurl= realurl + (window.isWebp ? "@!webp" : "");
          

          //console.log(realurl);
          //alert(realurl);   
                  
       }



       return realurl;

}

//获取cococomic当前图片

function getkekerealurl(urlstr){
       var realurl=urlstr;
       var ServerList=new Array(16);
ServerList[0]="http://2.99manga.com:9393/dm01/";
ServerList[1]="http://2.99manga.com:9393/dm02/";
ServerList[2]="http://2.99manga.com:9393/dm03/";
ServerList[3]="http://2.99manga.com:9393/dm04/";
ServerList[4]="http://2.99manga.com:9393/dm05/";
ServerList[5]="http://2.99manga.com:9393/dm06/";
ServerList[6]="http://2.99manga.com:9393/dm07/";
ServerList[7]="http://2.99manga.com:9393/dm08/";
ServerList[8]="http://2.99manga.com:9393/dm09/";
ServerList[9]="http://2.99manga.com:9393/dm10/";
ServerList[10]="http://2.99manga.com:9393/dm11/";
ServerList[11]="http://2.99manga.com:9393/dm12/";
ServerList[12]="http://2.99manga.com:9393/dm13/";
ServerList[13]="http://2.99manga.com:9393/dm14/";
ServerList[14]="http://2.99manga.com:9393/dm15/";
ServerList[15]="http://2.99manga.com:9393/dm16/";


       if(realurl.indexOf("/dm01/")!=-1){
    
          realurl=ServerList[0]+realurl.split("/dm01/")[1];
                                 
  }
       else if(realurl.indexOf("/dm02/")!=-1){

       realurl=ServerList[1]+realurl.split("/dm02/")[1];
        }
       else if(realurl.indexOf("/dm03/")!=-1){

       realurl=ServerList[2]+realurl.split("/dm03/")[1];
        }
       else if(realurl.indexOf("/dm04/")!=-1){

       realurl=ServerList[3]+realurl.split("/dm04/")[1];
        }
       else if(realurl.indexOf("/dm05/")!=-1){

       realurl=ServerList[4]+realurl.split("/dm05/")[1];
        }
       else if(realurl.indexOf("/dm06/")!=-1){

       realurl=ServerList[5]+realurl.split("/dm06/")[1];
        }
       else if(realurl.indexOf("/dm07/")!=-1){

       realurl=ServerList[6]+realurl.split("/dm07/")[1];
        }
       else if(realurl.indexOf("/dm08/")!=-1){

       realurl=ServerList[7]+realurl.split("/dm08/")[1];
        }
       else if(realurl.indexOf("/dm09/")!=-1){

       realurl=ServerList[8]+realurl.split("/dm09/")[1];
        }
       else if(realurl.indexOf("/dm10/")!=-1){

       realurl=ServerList[9]+realurl.split("/dm10/")[1];
        }
       else if(realurl.indexOf("/dm11/")!=-1){

       realurl=ServerList[10]+realurl.split("/dm11/")[1];
        }
       else if(realurl.indexOf("/dm12/")!=-1){

       realurl=ServerList[11]+realurl.split("/dm12/")[1];
        }
       else if(realurl.indexOf("/dm13/")!=-1){

       realurl=ServerList[12]+realurl.split("/dm13/")[1];
        }
       else if(realurl.indexOf("/dm14/")!=-1){

       realurl=ServerList[14]+realurl.split("/dm14/")[1];
        }
       else if(realurl.indexOf("/dm15/")!=-1){

       realurl=ServerList[14]+realurl.split("/dm15/")[1];
        }
       else{

       realurl=realurl;
        }



       return realurl;

}
function getremoteqqurl(qqurl)
{                
    // http://ac.tc.qq.com/store_file_download?buid=15017&uin=521341&dir_path=/mif800/8/99/519899/73/&name=1369.mif2;
    var bym="http://img11.hgysxz.cn"
    var v=qqurl;
    var qqurlarr=qqurl.split("dir_path=/");
    var qqfilename=qqurlarr[1].replace("&name=","");
    qqfilename=qqfilename.replace("mif2","jpg");
    qqfilename=qqfilename.replace("ori","jpg");
    qqfilename=qqfilename.replace(/\//g,"_");
    var u="http://img11.aoyuanba.com/pictmdown.php?p="+base64_encode(v)+"&sf="+qqfilename+"&ym="+bym;
    //alert(u);
    return u;
}
function getcurpic(i){
         
        
        //alert(getUrlpics()[i]);    
  
        var v=getUrlpics()[i];
        var v1="";
        var s="";
         
        if(v.indexOf("qq.com/store_file_download")!=-1){

                //alert(v);
                s=getremoteqqurl(v);
        }
        else if (v.indexOf("/ok-comic")!=-1){
                   v=getkekerealurl(v);

                     //alert(v);
       s="http://img5.aoyuanba.com/pictmdown.php?p="+base64_encode(v);
        }
        else if (v.indexOf("mangafiles.com")!=-1){

    s="http://img6.aoyuanba.com:8056/pictmdown.php?p="+base64_encode(v);
        } 
        else if (v.indexOf("imgs.gengxin123.com")!=-1){
                var bym="http://www.kxdm.com/";
                v1=v.replace("imgs.gengxin123.com","imgs1.ysryd.com");
    s="http://imgsty1.aoyuanba.com/pictmdown.php?bu="+bym+"&p="+base64_encode(v1); 
                    
        } 
        else if (v.indexOf("imgs1.ysryd.com")!=-1){
                var bym="http://www.kxdm.com/";
    s="http://imgsty1.aoyuanba.com/pictmdown.php?bu="+bym+"&p="+base64_encode(v);
               
        } 
        else if (v.indexOf("dmzj.com")!=-1){
                var bym="http://manhua.dmzj.com/";
                v=encodeURI(v);
                 
                 //alert(v);
    s="http://imgsty.aoyuanba.com/pictmdown.php?bu="+bym+"&p="+base64_encode(v);
        } 
        else if (v.indexOf("imgsrc.baidu.com")!=-1){

    //s="http://www.mh160.com/qTcms_Inc/qTcms.Pic.FangDao.asp?p="+base64_encode(v);
                  s="http://img7.aoyuanba.com/picinc/qTcms.Pic.FangDao.asp?p="+base64_encode(v);
        } 
        else if (v.indexOf("sinaimg.cn")!=-1){

                s="http://img7.aoyuanba.com/picinc/qTcms.Pic.FangDao.asp?p="+base64_encode(v); 
        } 
        else if (v.indexOf("jumpcn.cc")!=-1){

                s="http://img7.aoyuanba.com/picinc/qTcms.Pic.FangDao.asp?p="+base64_encode(v); 
        } 
        else if (v.indexOf("bbs.zymk.cn")!=-1){ 
                  s="http://img7.aoyuanba.com/picinc/qTcms.Pic.FangDao.asp?p="+base64_encode(v);
        }
        else if (v.indexOf("zhujios.com")!=-1){
    
                 s="http://img8.hgysxz.cn/picinc/qTcms.Pic.FangDao.asp?p="+base64_encode(v);
       } 
       else if (v.indexOf("cartoon.akshk.com")!=-1){
    
                 s="http://img7.aoyuanba.com/picinc/qTcms.Pic.FangDao.asp?p="+base64_encode(v);
       }   
        else if (v.indexOf("JLmh160")!=-1){

                //s="http://img3.aoyuanba.com/picinc/qTcms.Pic.FangDao.asp?p="+base64_encode(v);      
                // s="http://img3.aoyuanba.com/mh160/"+v+".jpg";
                s="http://d.mh160.com/d/decode/?p="+v+"&bid="+parseInt(cid); 
        }   
                              
  else{
           
        s=getrealurl(v);

        } 
  return s
  
}

function prom(vstr)  
{ 
    var name=prompt("请输入章节名称",vstr);//将输入的内容赋给变量 name ，   
    if(name)//如果返回的有内容 
  
    { 
         
     } 
  
}


function getpicdamin()  
{ 
    //if (parseInt(cid)>10000){
      
         //yuming="https://mhpic6.hsvac.cn";
        //yuming="https://manhuapicdisk03.cdn.bcebos.com";
     
   // }else{
     
        //yuming="https://mhpic7.kingwar.cn"; 
         // yuming="https://manhuapicdisk03.cdn.bcebos.com"; 
    //}
     
    //yuming="https://mhpic6.hsvac.cn";
     // yuming="https://mhpic6.szsjcd.cn";
      //yuming="https://mhpic6.miyeye.cn:20207";
       
       yuming="https://res.gezhengzhongyi.cn:8443";

    if (parseInt(currentChapterid)>542724){
         
         //yuming="https://mhpic5.miyeye.cn:8443";
         yuming="https://mhpic5.gezhengzhongyi.cn:8443";
         //yuming="https://mhpic5.hsvac.cn";
        //yuming="https://manhuapicdisk02.cdn.bcebos.com";
     
    }
    if (parseInt(currentChapterid)>885032)      
       yuming="https://mhpic88.miyeye.cn:8443";
   



    return yuming; 
}



function base64_decode (data) {
    var b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
    var o1, o2, o3, h1, h2, h3, h4, bits, i = 0, ac = 0, dec = "", tmp_arr = [];
    if (!data) {return data;}
    data += '';
    do { 
        h1 = b64.indexOf(data.charAt(i++));
        h2 = b64.indexOf(data.charAt(i++));
        h3 = b64.indexOf(data.charAt(i++));
        h4 = b64.indexOf(data.charAt(i++));
        bits = h1<<18 | h2<<12 | h3<<6 | h4;
        o1 = bits>>16 & 0xff;
        o2 = bits>>8 & 0xff;
        o3 = bits & 0xff;
        if (h3 == 64) {
            tmp_arr[ac++] = String.fromCharCode(o1);
        } else if (h4 == 64) {
            tmp_arr[ac++] = String.fromCharCode(o1, o2);
        } else {
            tmp_arr[ac++] = String.fromCharCode(o1, o2, o3);
        }
    } while (i < data.length);
    dec = tmp_arr.join('');
    dec = utf8_decode(dec);
    return dec;
}

function base64_encode (data) {
    var b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
    var o1, o2, o3, h1, h2, h3, h4, bits, i = 0, ac = 0, enc="", tmp_arr = [];
    if (!data){return data;}
    data = utf8_encode(data+'');
    do {
        o1 = data.charCodeAt(i++);
        o2 = data.charCodeAt(i++);
        o3 = data.charCodeAt(i++);
        bits = o1<<16 | o2<<8 | o3;
        h1 = bits>>18 & 0x3f;
        h2 = bits>>12 & 0x3f;
        h3 = bits>>6 & 0x3f;
        h4 = bits & 0x3f;
        tmp_arr[ac++] = b64.charAt(h1) + b64.charAt(h2) + b64.charAt(h3) + b64.charAt(h4);
    } while (i < data.length);
    enc = tmp_arr.join('');
    switch (data.length % 3) {
        case 1:
            enc = enc.slice(0, -2) + '==';
        break;
        case 2:
            enc = enc.slice(0, -1) + '=';
        break;
    }
    return enc;
}
function utf8_decode ( str_data ) {
    var tmp_arr = [], i = 0, ac = 0, c1 = 0, c2 = 0, c3 = 0;
    str_data += '';
    while ( i < str_data.length ) {
        c1 = str_data.charCodeAt(i);
        if (c1 < 128) {
            tmp_arr[ac++] = String.fromCharCode(c1);
            i++;
        } else if ((c1 > 191) && (c1 < 224)) {
            c2 = str_data.charCodeAt(i+1);
            tmp_arr[ac++] = String.fromCharCode(((c1 & 31) << 6) | (c2 & 63));
            i += 2;
        } else {
            c2 = str_data.charCodeAt(i+1);
            c3 = str_data.charCodeAt(i+2);
            tmp_arr[ac++] = String.fromCharCode(((c1 & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
            i += 3;
        }
    }
    return tmp_arr.join('');
}

function utf8_encode ( argString ) {
    var string = (argString+''); 
    var utftext = "";
    var start, end;
    var stringl = 0;
    start = end = 0;
    stringl = string.length;
    for (var n = 0; n < stringl; n++) {
        var c1 = string.charCodeAt(n);
        var enc = null;
        if (c1 < 128) {
            end++;
        } else if (c1 > 127 && c1 < 2048) {
            enc = String.fromCharCode((c1 >> 6) | 192) + String.fromCharCode((c1 & 63) | 128);
        } else {
            enc = String.fromCharCode((c1 >> 12) | 224) + String.fromCharCode(((c1 >> 6) & 63) | 128) + String.fromCharCode((c1 & 63) | 128);
        }
        if (enc !== null) {
            if (end > start) {
                utftext += string.substring(start, end);
            }
            utftext += enc;
            start = end = n+1;
        }
    }
    if (end > start) {
        utftext += string.substring(start, string.length);
    }
    return utftext;
}
