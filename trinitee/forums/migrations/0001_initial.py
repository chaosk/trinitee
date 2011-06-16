# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Category'
        db.create_table('forums_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forums.Category'], null=True, blank=True)),
            ('ordering', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('forums', ['Category'])

        # Adding model 'Topic'
        db.create_table('forums_topic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='created_topics', to=orm['auth.User'])),
            ('modified_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='modified_topics', null=True, to=orm['auth.User'])),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forums.Category'])),
            ('is_closed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_sticky', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('first_post', self.gf('django.db.models.fields.related.OneToOneField')(related_name='topic_root', unique=True, to=orm['forums.Post'])),
        ))
        db.send_create_signal('forums', ['Topic'])

        # Adding model 'Post'
        db.create_table('forums_post', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('topic', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forums.Topic'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='created_posts', to=orm['auth.User'])),
            ('modified_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='modified_posts', null=True, to=orm['auth.User'])),
            ('show_edits', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('content_html', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('forums', ['Post'])

        # Adding model 'PostKarma'
        db.create_table('forums_postkarma', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('post', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forums.Post'])),
            ('karma', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('forums', ['PostKarma'])

        # Adding unique constraint on 'PostKarma', fields ['user', 'post']
        db.create_unique('forums_postkarma', ['user_id', 'post_id'])

        # Adding model 'Poll'
        db.create_table('forums_poll', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='polls_started', to=orm['auth.User'])),
            ('expires_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('question', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('topic', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forums.Topic'])),
            ('max_votes', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
        ))
        db.send_create_signal('forums', ['Poll'])

        # Adding model 'Choice'
        db.create_table('forums_choice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('poll', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forums.Poll'])),
            ('choice', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('forums', ['Choice'])

        # Adding model 'Vote'
        db.create_table('forums_vote', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('poll', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forums.Poll'])),
            ('choice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forums.Choice'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('forums', ['Vote'])

        # Adding unique constraint on 'Vote', fields ['poll', 'choice', 'user']
        db.create_unique('forums_vote', ['poll_id', 'choice_id', 'user_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Vote', fields ['poll', 'choice', 'user']
        db.delete_unique('forums_vote', ['poll_id', 'choice_id', 'user_id'])

        # Removing unique constraint on 'PostKarma', fields ['user', 'post']
        db.delete_unique('forums_postkarma', ['user_id', 'post_id'])

        # Deleting model 'Category'
        db.delete_table('forums_category')

        # Deleting model 'Topic'
        db.delete_table('forums_topic')

        # Deleting model 'Post'
        db.delete_table('forums_post')

        # Deleting model 'PostKarma'
        db.delete_table('forums_postkarma')

        # Deleting model 'Poll'
        db.delete_table('forums_poll')

        # Deleting model 'Choice'
        db.delete_table('forums_choice')

        # Deleting model 'Vote'
        db.delete_table('forums_vote')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'forums.category': {
            'Meta': {'object_name': 'Category'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forums.Category']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'forums.choice': {
            'Meta': {'object_name': 'Choice'},
            'choice': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'poll': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forums.Poll']"})
        },
        'forums.poll': {
            'Meta': {'object_name': 'Poll'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polls_started'", 'to': "orm['auth.User']"}),
            'expires_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_votes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forums.Topic']"})
        },
        'forums.post': {
            'Meta': {'object_name': 'Post'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'content_html': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_posts'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'modified_posts'", 'null': 'True', 'to': "orm['auth.User']"}),
            'show_edits': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forums.Topic']"})
        },
        'forums.postkarma': {
            'Meta': {'unique_together': "(('user', 'post'),)", 'object_name': 'PostKarma'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'karma': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forums.Post']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'forums.topic': {
            'Meta': {'object_name': 'Topic'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forums.Category']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_topics'", 'to': "orm['auth.User']"}),
            'first_post': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'topic_root'", 'unique': 'True', 'to': "orm['forums.Post']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_sticky': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'modified_topics'", 'null': 'True', 'to': "orm['auth.User']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'forums.vote': {
            'Meta': {'unique_together': "(('poll', 'choice', 'user'),)", 'object_name': 'Vote'},
            'choice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forums.Choice']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'poll': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forums.Poll']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['forums']
