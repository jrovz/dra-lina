"""
Celery tasks for async AI operations.
"""
import logging
from celery_app import celery

logger = logging.getLogger(__name__)


@celery.task(bind=True, name='ai.research_topic')
def research_topic_task(self, topic, model='gpt-5.2'):
    from utils.ai_services import research_topic
    logger.info("Task %s: researching '%s' with model %s", self.request.id, topic, model)
    return research_topic(topic, model=model)


@celery.task(bind=True, name='ai.generate_draft')
def generate_draft_task(self, topic, model='gpt-5.2', research=None):
    from utils.ai_services import generate_blog_draft
    logger.info("Task %s: generating draft for '%s'", self.request.id, topic)
    return generate_blog_draft(topic, model=model, research=research)


@celery.task(bind=True, name='ai.generate_image')
def generate_image_task(self, title, model='dall-e-3'):
    from utils.ai_services import generate_featured_image
    logger.info("Task %s: generating image for '%s'", self.request.id, title)
    return generate_featured_image(title, model=model)
