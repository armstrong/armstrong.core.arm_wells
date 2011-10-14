window.Node = window.Item.extend({
    url: "",
});

window.NodeList = Backbone.Collection.extend({
    url: "",
    model: window.Node,
    parseForm: function(prefix) {
        var forms = $('#' + prefix + '-forms');
        var list = this;
        forms.children().each(function(idx, el){
            var node = new window.Node({prefix: el.id+"-"});
            list.add(node);
        });
    },
    comparator: function(node) {
        return node.get("order");
    }
});

window.ManagementForm = Backbone.View.extend({
    initialize: function() {
        this.options.collection.bind("reset", this.update, this);
        this.options.collection.bind("add", this.update, this);
        this.options.collection.bind("remove", this.update, this);
    },
    update: function() {
        $("id_"+this.options.prefix+"-TOTAL_FORMS").val(this.options.collection.length);
    }
})

window.NodeListItemView = Backbone.View.extend({
    tagName: "div",
    className: "node-inline",
    initialize: function() {
        this.model.bind('change', this.render, this);
    },
    render: function() {
        var html = this.options.template(this.model);
        $(this.el).html(html);
        return this;
    }
});

window.NodeListView = Backbone.View.extend({
    tagName: "div",
    initialize: function() {
        if (!this.collection) {
            this.collection = new window.NodeList;
            this.collection.parseForm(this.options.prefix);
        }
        this.options.managementForm = new window.ManagementForm({
            prefix: this.options.prefix,
            collection: this.collection
        });
        $(this.el).sortable();
        // note jQuery bind, not backbone
        var self = this;
        $(this.el).bind('sortupdate', function(){self.sorted();});
    },
    addOne: function(node) {
        var view = new window.NodeListItemView({
                model: node,
                id: node.cid,
                prefix: this.options.prefix,
                template: _.template($('#nodes-list-item-template').html())
            });
        $(this.el).append(view.render().el);
    },
    addAll: function() {
        for(i=0; i<this.collection.length; i++){
            this.addOne(this.collection.at(i));
        }
    },
    addFromForm: function() {
        var selector = "input[id^='id_" + this.options.prefix + "-__prefix__']"
        var sourceForm = $(selector);
        var formId = this.collection.length;
        var formDiv = $('<div id="' + this.options.prefix + '-' + formId + '" class="' + this.options.prefix + '-object"></div>');
        $("#" + this.options.prefix + "-forms").append(formDiv);
        sourceForm.each(function(idx, el) {
            el = $(el);
            var newEl = el.clone();
            newEl.attr('id', el.attr('id').replace('__prefix__', formId));
            newEl.attr('name', el.attr('name').replace('__prefix__', formId));
            newEl.attr('type', 'hidden')
            formDiv.append(newEl);
        });
        var node = new window.Node({prefix: this.options.prefix+"-"+formId+"-"});
        node.parse();
        this.collection.add(node);
        this.addOne(node);
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
