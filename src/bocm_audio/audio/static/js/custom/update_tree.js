/**
 * Created by PyCharm.
 * User: daitr
 * Date: 13-6-6
 * Time: 下午11:15
 * To change this template use File | Settings | File Templates.
 */

/**
 * 更新所有的组织树
 */
function add_org_node(parrent_node,child_node){
    var org_zTree = $.fn.zTree.getZTreeObj("org_tree");
    if(org_zTree!=null){
        org_zTree.addNodes(parrent_node,child_node );
    };
    var user_org_zTree = $.fn.zTree.getZTreeObj("user_org_tree");
    if(user_org_zTree!=null){
        user_org_zTree.addNodes(parrent_node,child_node );
    };
    var term_org_zTree = $.fn.zTree.getZTreeObj("terminal_org_tree");
    if(term_org_zTree!=null){
        term_org_zTree.addNodes(parrent_node,child_node );
    };
}

function org_dialogAjaxDone(json){
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
        alert("orgasdfasdfasdf ");
    }
}


