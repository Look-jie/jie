/**
 * Created by Administrator on 2016/6/15.
 */
var options = {
    'width': 800,
    'height': 250,
    //上传图片的解析路径？？？
    uploadJson: '/admin/upload/kindeditor'
};
KindEditor.ready(function (K) {
    K.create('#id_content',options);
    
});