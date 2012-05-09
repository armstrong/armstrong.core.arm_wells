Node = Item.extend({
    url: ""
});

NodeList = ItemList.extend({
    model: Node,
    comparator: function(node) {
        return parseInt(node.get("order"), 10);
    }
});

NodeListItemView = ListItemView.extend({
    className: "node-inline"
});

NodeListView = SortableListView.extend({
    model_class: Node,
    list_item_view_class: NodeListItemView,
    collection_class: NodeList
});
