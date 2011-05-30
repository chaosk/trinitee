# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'WikiPage.title'
        db.alter_column('wiki_wikipage', 'title', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255))

        # Adding unique constraint on 'WikiPage', fields ['title']
        db.create_unique('wiki_wikipage', ['title'])

        # Adding unique constraint on 'WikiPage', fields ['slug']
        db.create_unique('wiki_wikipage', ['slug'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'WikiPage', fields ['slug']
        db.delete_unique('wiki_wikipage', ['slug'])

        # Removing unique constraint on 'WikiPage', fields ['title']
        db.delete_unique('wiki_wikipage', ['title'])

        # Changing field 'WikiPage.title'
        db.alter_column('wiki_wikipage', 'title', self.gf('django.db.models.fields.CharField')(max_length=50))


    models = {
        'wiki.wikipage': {
            'Meta': {'object_name': 'WikiPage'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'content_html': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['wiki']
