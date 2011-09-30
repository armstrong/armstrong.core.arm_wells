# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'WellType'
        db.create_table('arm_wells_welltype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
        ))
        db.send_create_signal('arm_wells', ['WellType'])

        # Adding model 'Well'
        db.create_table('arm_wells_well', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['arm_wells.WellType'])),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('expires', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('arm_wells', ['Well'])

        # Adding model 'Node'
        db.create_table('arm_wells_node', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('well', self.gf('django.db.models.fields.related.ForeignKey')(related_name='nodes', to=orm['arm_wells.Well'])),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('arm_wells', ['Node'])


    def backwards(self, orm):
        
        # Deleting model 'WellType'
        db.delete_table('arm_wells_welltype')

        # Deleting model 'Well'
        db.delete_table('arm_wells_well')

        # Deleting model 'Node'
        db.delete_table('arm_wells_node')


    models = {
        'arm_wells.node': {
            'Meta': {'ordering': "['order']", 'object_name': 'Node'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'well': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'nodes'", 'to': "orm['arm_wells.Well']"})
        },
        'arm_wells.well': {
            'Meta': {'object_name': 'Well'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'expires': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['arm_wells.WellType']"})
        },
        'arm_wells.welltype': {
            'Meta': {'object_name': 'WellType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['arm_wells']
