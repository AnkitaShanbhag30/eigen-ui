#!/usr/bin/env python3
"""
Enhanced Template System Demo
Showcases the new modular, configurable templates with rich brand integration
"""

import json
import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a CLI command and show results"""
    print(f"\n{'='*60}")
    print(f"🎯 {description}")
    print(f"{'='*60}")
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Success!")
            if result.stdout:
                print("Output:")
                print(result.stdout)
        else:
            print("❌ Failed!")
            if result.stderr:
                print("Error:")
                print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("🚀 Enhanced Template System Demo")
    print("This demo showcases the new modular, configurable templates")
    
    # Check if we have a brand to work with
    if not os.path.exists("data/brands/gigit.json"):
        print("❌ Brand 'gigit' not found. Please run 'python cli.py ingest <url> gigit' first.")
        return
    
    # Demo 1: Basic rendering with custom content
    print("\n" + "="*80)
    print("📊 DEMO 1: Basic Rendering with Custom Content")
    print("="*80)
    
    run_command(
        'python cli.py render gigit onepager --format png --title "Product Launch" --subtitle "Revolutionary new features" --cta "Learn More"',
        "Basic PNG rendering with custom title, subtitle, and CTA"
    )
    
    # Demo 2: KPI and metrics display
    print("\n" + "="*80)
    print("📈 DEMO 2: KPI and Metrics Display")
    print("="*80)
    
    run_command(
        'python cli.py render gigit onepager --format png --title "Q3 Results" --kpis "Monthly Users:15K,Revenue:$75K,Churn Rate:2%,NPS Score:85"',
        "PNG rendering with KPI metrics display"
    )
    
    # Demo 3: Custom bullet points
    print("\n" + "="*80)
    print("📝 DEMO 3: Custom Bullet Points")
    print("="*80)
    
    run_command(
        'python cli.py render gigit onepager --format png --title "Feature Overview" --bullets "Easy to use;Fast setup;24/7 support;Mobile friendly;API access;Real-time analytics"',
        "PNG rendering with custom bullet points"
    )
    
    # Demo 4: Advanced custom sections
    print("\n" + "="*80)
    print("🎨 DEMO 4: Advanced Custom Sections")
    print("="*80)
    
    # Create a complex sections JSON
    sections_data = [
        {
            "title": "Key Features",
            "type": "bullets",
            "bullets": ["AI-powered insights", "Real-time analytics", "Mobile-first design"]
        },
        {
            "title": "Performance Metrics",
            "type": "grid",
            "columns": 3,
            "items": [
                {"icon": "🚀", "title": "Speed", "value": "10x faster", "description": "Lightning quick performance"},
                {"icon": "📊", "title": "Accuracy", "value": "99.9%", "description": "Near-perfect precision"},
                {"icon": "🔄", "title": "Uptime", "value": "99.99%", "description": "Enterprise-grade reliability"}
            ]
        },
        {
            "title": "Customer Testimonial",
            "type": "quote",
            "quote": "This product transformed our entire workflow!",
            "author": "Sarah Johnson, CTO"
        }
    ]
    
    sections_json = json.dumps(sections_data).replace('"', '\\"')
    
    run_command(
        f'python cli.py render gigit onepager --format png --title "Advanced Demo" --sections "{sections_json}"',
        "PNG rendering with advanced custom sections (bullets, grid, quote)"
    )
    
    # Demo 5: PDF rendering
    print("\n" + "="*80)
    print("📄 DEMO 5: PDF Rendering")
    print("="*80)
    
    run_command(
        'python cli.py render gigit onepager --format pdf --title "Executive Summary" --subtitle "Q3 2024 Performance Review" --cta "Schedule Demo" --output "executive-summary.pdf"',
        "PDF rendering with custom content"
    )
    
    # Demo 6: High-resolution PNG
    print("\n" + "="*80)
    print("🖼️ DEMO 6: High-Resolution PNG")
    print("="*80)
    
    run_command(
        'python cli.py render gigit onepager --format png --title "High-Res Demo" --width 2400 --height 3200 --scale 3 --output "high-res-demo.png"',
        "High-resolution PNG rendering (2400x3200, 3x scale)"
    )
    
    # Demo 7: Brand integration showcase
    print("\n" + "="*80)
    print("🎨 DEMO 7: Brand Integration Showcase")
    print("="*80)
    
    run_command(
        'python cli.py show-brand gigit',
        "Show brand identity details"
    )
    
    run_command(
        'python cli.py design-tokens gigit',
        "Show generated design tokens"
    )
    
    # Summary
    print("\n" + "="*80)
    print("🎉 DEMO COMPLETE!")
    print("="*80)
    print("Generated files:")
    
    try:
        files = [f for f in os.listdir('.') if f.endswith(('.png', '.pdf'))]
        for file in sorted(files):
            size = os.path.getsize(file) / 1024
            print(f"  📁 {file} ({size:.1f} KB)")
    except Exception as e:
        print(f"Could not list files: {e}")
    
    print("\n✨ Key Features Demonstrated:")
    print("  • Dynamic brand color integration")
    print("  • Modular content sections")
    print("  • KPI and metrics display")
    print("  • Custom bullet points")
    print("  • Grid layouts with icons")
    print("  • Quote/testimonial sections")
    print("  • High-resolution rendering")
    print("  • Multiple output formats")
    print("  • Responsive design")
    
    print("\n🚀 Next Steps:")
    print("  • Try different brand slugs")
    print("  • Experiment with custom section types")
    print("  • Create your own templates")
    print("  • Use the API for automation")

if __name__ == "__main__":
    main()
