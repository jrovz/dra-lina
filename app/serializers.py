"""
Marshmallow schemas for consistent API serialization.
"""
from marshmallow import Schema, fields


class PaginationSchema(Schema):
    page = fields.Integer()
    per_page = fields.Integer()
    total = fields.Integer()
    pages = fields.Integer()


class ServiceSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    duration_minutes = fields.Integer()
    price = fields.Float(required=True)


class DoctorSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String()
    name = fields.String()
    specialty = fields.String()
    bio = fields.String()
    color = fields.String()


class BlogPostSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True)
    slug = fields.String()
    content = fields.String()
    featured_image_url = fields.String()
    seo_keywords = fields.String()
    references = fields.String()
    category = fields.String()
    created_at = fields.DateTime(format='%Y-%m-%dT%H:%M:%S')
    updated_at = fields.DateTime(format='%Y-%m-%dT%H:%M:%S')
    is_published = fields.Boolean()


class BlogPostListSchema(Schema):
    """Lightweight schema for list views (no content body)."""
    id = fields.Integer(dump_only=True)
    title = fields.String()
    slug = fields.String()
    featured_image_url = fields.String()
    category = fields.String()
    created_at = fields.DateTime(format='%Y-%m-%dT%H:%M:%S')
    is_published = fields.Boolean()


class AppointmentSchema(Schema):
    id = fields.Integer(dump_only=True)
    patient_name = fields.String()
    service_name = fields.String()
    doctor_name = fields.String()
    start_time = fields.DateTime(format='%Y-%m-%dT%H:%M:%S')
    status = fields.String()
    created_at = fields.DateTime(format='%Y-%m-%dT%H:%M:%S')


class PatientSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    document_id = fields.String(required=True)
    email = fields.String()
    phone = fields.String(required=True)
    age = fields.Integer(required=True)


class DashboardStatsSchema(Schema):
    appointments_today = fields.Integer()
    appointments_pending = fields.Integer()
    posts_published = fields.Integer()
    posts_draft = fields.Integer()
    doctors_count = fields.Integer()
    patients_count = fields.Integer()


# Singleton instances
service_schema = ServiceSchema()
services_schema = ServiceSchema(many=True)
doctor_schema = DoctorSchema()
doctors_schema = DoctorSchema(many=True)
post_schema = BlogPostSchema()
posts_schema = BlogPostSchema(many=True)
post_list_schema = BlogPostListSchema(many=True)
appointment_schema = AppointmentSchema()
appointments_schema = AppointmentSchema(many=True)
patient_schema = PatientSchema()
dashboard_stats_schema = DashboardStatsSchema()
