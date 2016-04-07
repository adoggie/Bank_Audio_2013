/**
 * Created by PyCharm.
 * User: daitr
 * Date: 13-5-13
 * Time: 下午5:27
 * To change this template use File | Settings | File Templates.
 */


/**
 * dialog上的表单提交回调函数
 * 服务器转回navTabId，可以重新载入指定的navTab. statusCode=DWZ.statusCode.ok表示操作成功, 自动关闭当前dialog
 * form提交后返回json数据结构,json格式和navTabAjaxDone一致
 */
function dialogAjaxDone(json){
    DWZ.ajaxDone(json);
    if (json.statusCode == DWZ.statusCode.ok){
        if (json.navTabId){
            navTab.reload(json.forwardUrl, {navTabId: json.navTabId});
        } else if (json.rel) {
            var $pagerForm = $("#pagerForm", navTab.getCurrentPanel());
            var args = $pagerForm.size()>0 ? $pagerForm.serializeArray() : {}
            navTabPageBreak(args, json.rel);
        }
        if ("closeCurrent" == json.callbackType) {
            $.pdialog.closeCurrent();
        }
    }
}
/**
 *custom上的表单提交回调函数
 * 服务器转回navTabId，可以重新载入指定的navTab. statusCode=DWZ.statusCode.ok表示操作成功, 自动关闭当前custom
 * form提交后返回json数据结构,json格式和navTabAjaxDone一致
 */
function customAjaxDone(json){
    DWZ.ajaxDone(json);
    if (json.statusCode == DWZ.statusCode.ok){
        if (json.navTabId){
            navTab.reload(json.forwardUrl, {navTabId: json.navTabId});
        } else if (json.rel) {
            var $pagerForm = $("#pagerForm", navTab.getCurrentPanel());
            var args = $pagerForm.size()>0 ? $pagerForm.serializeArray() : {}
            navTabPageBreak(args, json.rel);
        }
        if ("closeCurrent" == json.callbackType) {
            $.pcustom.closeCurrent();
        }
    }
}
