var CryptoJS = require('crypto-js')
// var __READKEY = 'fw12558899ertyui';


function __cdecrypt(key, word) {
  var key = CryptoJS.enc.Utf8.parse(key);
  var decrypt = CryptoJS.AES.decrypt(word, key, {
    mode: CryptoJS.mode.ECB,
    padding: CryptoJS.pad.Pkcs7
  });
  return CryptoJS.enc.Utf8.stringify(decrypt).toString()
};

function decode_data(C_DATA, key, default_key) {
  // console.log(C_DATA);
  // @see https://www.ohmanhua.com/js/custom.js
  C_DATA = CryptoJS.enc.Base64.parse(C_DATA).toString(
      CryptoJS.enc.Utf8);

  var KEY_list = [ 'fw122587mkertyui', 'fw12558899ertyui',
        'JRUIFMVJDIWE569j' ];
  if (typeof default_key === 'string' && default_key){
      KEY_list.unshift(default_key);
  }
  if (key){
      KEY_list.unshift(key);
  }

  for (var index = 0; index < KEY_list.length; index++) {
      // @search `if (typeof C_DATA !=` ...) { eval( @
      // https://www.ohmanhua.com/js/custom.js
      try {
          var DECRIPT_DATA = __cdecrypt(KEY_list[index],
                  C_DATA);
          if (DECRIPT_DATA)
              return DECRIPT_DATA;
      } catch (e) {
        console.log("decode_data error");
      }
  }
}


function decode(C_DATA) {
  C_DATA = decode_data(C_DATA);
  console.log(C_DATA);

  var mh_info, image_info;
  eval(C_DATA);
  mh_info.image_info = image_info;
  // @see `totalImageCount =
  // parseInt(eval(base64[__Ox97c0e[0x4]](__Ox97c0e[0x3])))` @
  // https://www.ohmanhua.com/js/manga.read.js
  if (mh_info.enc_code1) {
    mh_info.totalimg = eval(decode_data(mh_info.enc_code1));
  }
  if (mh_info.enc_code2) {
    mh_info.imgpath = decode_data(mh_info.enc_code2,
        // 2020/9/3 改版
        // @see function __cr_getpice(_0xfb06x4a)
        "fw125gjdi9ertyui", "");
  }
  return mh_info;
}

function getArr(data) {
  var using_webp = false
  var base_URL = 'https://www.cocomanhua.com/'
  var chapter_data = {}
  if (!chapter_data || !(chapter_data = decode(data))) {
    CeL.warn(work_data.title + ' #' + chapter_NO
        + ': No valid chapter data got!');
    return;
  }
// chapter_data.startimg often "1"
  var image_NO = parseInt(chapter_data.startimg) || 1;
// 設定必要的屬性。
  chapter_data.title = chapter_data.pagename;
// chapter_data.image_count = chapter_data.totalimg + image_NO - 1;

// @see function __cr_getpice() @
// https://www.ohmanhua.com/js/manga.read.js
  var chapter_image_base_path = base_URL.replace(/:\/\/.+/, '://')
      // "img.mljzmm.com"
      + chapter_data.domain + "/comic/" + encodeURI(chapter_data.imgpath);
  chapter_data.image_list = [];

  for (; image_NO <= chapter_data.totalimg; image_NO++) {
    // @see __cr.PrefixInteger()
    var image_url = chapter_image_base_path + (Array(4).join("0") + image_NO).slice(-4) + ".jpg";
    if (using_webp) {
      // @see __cr.switchWebp()
      image_url += '.webp';
    }
    chapter_data.image_list.push(image_url);
  }
//
// mh_info = {
//   startimg: 1,
//   enc_code1: "aVp6aWlITE1XcGJmSllMd0Z2NFhIZz09",
//   mhid: "10330",
//   enc_code2: "dzNaUXJ5SXFUangvNFZDQzZPdjRFSGpsMEVyYzdtTFdNMUsyR2pXcHIzWVRuTGxqZlVYTkFwenhxWENDajVrYXlvS0ZOQkV1T0w3N0pDTDFneHhkblpobkwyWWx4ank3c0tCZ3ZDUk05c1k9",
//   mhname: "未婚爸爸",
//   pageid: 2823662,
//   pagename: "二十几个壮汉",
//   pageurl: "1/205.html",
//   readmode: 3,
//   maxpreload: 5,
//   defaultminline: 1,
//   domain: "img.cocomanhua.com",
//   manga_size: "",
//   default_price: 0,
//   price: 0
// };
//   console.log(chapter_data.image_list);
  return chapter_data.image_list
}

// var data = "a29ydGl3RktIZSs2WGhPS3M4ZW1yNmhsaWowT0szeGZERTRTYmNhN1RPYTYxbmNWN0ZmV3VqL1ozMFkwZFZ3KzJlTU1vT2JVcEgyeW1nVVRVUmQ4OWJhNU55VkFaamp2ODYyZTFEQXQwYWM5eDBWbWxnSmdJUTJTd0NwY1dFUndPbFBWVFBwQ3E0NzY0SXpqZnlBdjJIM1ViK2J0Um1oZ1pQZTAyMS84dGloUDhWb21FOHVYTzRzSGYvZitDb3dicU1aWEFLQzJQd1A3NXlONkc4bmJiNzB5U2cxbFdwMjV0U1E3NXZQT1JwKzJwY1RFRFl1dWFOSFdCRUlOS0I1aFZJbVZtNlM0czZLd3Q5M1FuVU1zSFlWTGV0aFJHL0didWlJWWM4TldreHIyWnRML0lYcmF2SHlBcEYzTTVHMTFPM295UWVLS3hKVGJrRXJ2YTFPeWtWQVVkaUhoc0hCdjVJV2RDdGIzZVdpaEtVQ1pISVRrSTBBWjRpUEhDZ1pRUm5TQXI2K3l3cnlreTJTclM5U0VMTVRISVJVRjJNQ3B2VnlxbDQ3QjI4blBxb2ViSUtRd0JFeWZhQ20rVDFMK1ZpbnVUMjNES0E0NmF5ckRsUnhJazJ6YUZ2UGNJVHU2a21OQXJKZlFjUnZsUXB6YmhyUWlpYi9HVW1ldFpHd2VTbjZlZk9VTWh3cmpLdkhNOXI2SGFQd2wvTU1TS1UrSFQxL0lFMGhXUyt6THRic0NaOVMxc1dNVUtsZ1VEOWdkWERyOEFib2tlbFVwRy9yekMvbEc0VHV2aHg2eEhiR0pNeFNMYXVMaTFWNEJJbzUxQ3ljWDBFVUMyWE9Gd1A5S3BBMHAvNWJIMlpXWjNKb3d3MDh2bXFoYUI1SnFIeHJZSmtKbXV6WFRrQU09";

// console.log(getArr(data));
