"""
Services package initialization.
"""
from .booking import (
    get_available_slots,
    check_availability,
    generate_confirmation_token,
    confirm_token
)
from .ai_service import (
    research_topic,
    generate_blog_draft,
    generate_seo_metadata,
    refine_block_content,
    generate_featured_image,
    analyze_seo
)
