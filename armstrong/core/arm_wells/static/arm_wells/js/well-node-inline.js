window.Node = Backbone.Model.extend({
    url: "",
});

window.NodeList = Backbone.Collection.extend({
    url: "",
    model: window.Node
});

window.NodeListItemView = Backbone.View.extend({
    tagName: "div",
    render: function() {
        var html = this.options.template(this.model.toJSON());
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
                prefix: this.options.prefix,
                template: _.template(django.jQuery('#nodes-list-item-template').html()),
            });
        alert(this.options.target_id);
        django.jQuery(this.options.target_id).append(view.render().el);
    },
    addAll: function() {
        for(i=0; i<this.collection.length; i++){
            this.addOne(this.collection.at(i));
        }
    }
});
