window.Node = window.Item.extend({
    url: "",
});

window.NodeList = Backbone.Collection.extend({
    url: "",
    model: window.Node,
    parseForm: function(prefix) {
        var forms = django.jQuery('#' + prefix + '-forms');
        var list = this;
        forms.children().each(function(idx, el){
            var node = new window.Node({prefix: el.id+"-"});
            node.parse();
            list.add(node);
        });
    },
    comparator: function(node) {
        return node.get("order");
    }
});

window.NodeListItemView = Backbone.View.extend({
    tagName: "div",
    className: "node-inline",
    render: function() {
        var html = this.options.template(this.model);
        django.jQuery(this.el).html(html);
        return this;
    }
});

window.NodeListView = Backbone.View.extend({
    tagName: "div",
    render: function() {
        return this;
    },
    addOne: function(node) {
        var view = new window.NodeListItemView({
                model: node,
                id: node.cid,
                prefix: this.options.prefix,
                template: _.template(django.jQuery('#nodes-list-item-template').html())
            });
        django.jQuery(this.el).append(view.render().el);
    },
    addAll: function() {
        for(i=0; i<this.collection.length; i++){
            this.addOne(this.collection.at(i));
        }
    },
    sorted: function() {
        var self = this;
        var models = _.map($(this.el).children(), function(item){
            return self.collection.getByCid($(item).attr('id'));
        });
        _.each(models, function(model, idx, list) {
            model.set({'order': idx});
        });

    }
});
