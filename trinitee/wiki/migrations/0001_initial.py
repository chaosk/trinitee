# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'WikiPage'
        db.create_table('wiki_wikipage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('content_html', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('wiki', ['WikiPage'])


    def backwards(self, orm):
        
        # Deleting model 'WikiPage'
        db.delete_table('wiki_wikipage')


    models = {
        'wiki.wikipage': {
            'Meta': {'object_name': 'WikiPage'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'content_html': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['wiki']
