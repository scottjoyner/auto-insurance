/**
 * Document Service - Branding Assets Utility (Phase P1.2)
 * 
   Provides centralized management of organizational branding elements including:
   - Logo images (PNG/SVG)
   - Color schemes (primary, secondary, accent colors)
   - Font definitions for document types
   - Watermark configurations
 */

export interface BrandingAsset {
  type: 'logo' | 'color' | 'font' | 'watermark';
  key: string;
  format: 'png' | 'svg' | 'hex' | 'family';
  value?: any; // PNG/Buffer, HEX color code, font family name, etc.
}

/**
 * Branding Assets - Centralized Management Layer
 * 
   Provides centralized access to all organizational branding elements needed for
   consistent document generation including logos, colors, fonts, and watermarks.
 */
const brandingAssets: Record<string, BrandingAsset> = {
  // Logo assets
  'logo_primary': { type: 'logo', key: 'primary', format: 'png', value: null },
  'logo_secondary': { type: 'logo', key: 'secondary', format: 'svg', value: null },
  
  // Color scheme definitions
  'color_primary': { 
    type: 'color', 
    key: 'primary', 
    format: 'hex', 
    value: '#1B5E20' 
  }, // Green for insurance company
  'color_secondary': { 
    type: 'color', 
    key: 'secondary', 
    format: 'hex', 
    value: '#FFC107' 
  }, // Gold/yellow accent
  'color_accent': { 
    type: 'color', 
    key: 'accent', 
    format: 'hex', 
    value: '#42A5F5' 
  }, // Blue for links/buttons
  'color_background': { 
    type: 'color', 
    key: 'background', 
    format: 'hex', 
    value: '#FFFFFF' 
  }, // White background
  
  // Font definitions
  'font_document_body': { type: 'font', key: 'body', format: 'family', value: 'Helvetica, Arial, sans-serif' },
  'font_document_header': { type: 'font', key: 'header', format: 'family', value: 'Georgia, serif' },
  
  // Watermark configurations
  'watermark_disabled': { type: 'watermark', key: 'disabled', format: 'bool', value: false },
  'watermark_enabled': { type: 'watermark', key: 'enabled', format: 'png', value: null }
};

/**
 * Document Service - Branding Configuration Object
 * 
   Provides centralized access to all organizational branding elements needed for
   consistent document generation. This file serves as the single source of truth
   for all visual assets used across generated customer-facing documents.
 */
class BrandingConfiguration {
  /**
   * Get logo by type (primary or secondary)
   * @param type Logo variant to retrieve
   * @returns Logo data URL or path for document embedding
   */
  getLogo(type: 'primary' | 'secondary'): string | null {
    return brandingAssets[`${type}_logo`].value || null;
  }

  /**
   * Get color by key (primary, secondary, accent)
   * @param key Color identifier to retrieve
   * @returns Hex color code for styling elements
   */
  getColor(key: string): string {
    return brandingAssets[`${key}`].value || '#000000';
  }

  /**
   * Get font by usage (body, header)
   * @param usage Font usage type to retrieve
   * @returns Font family name for text rendering
   */
  getFont(usage: 'body' | 'header'): string {
    return brandingAssets[`${usage}`].value || '';
  }

  /**
   * Check if watermark is enabled in current configuration
   * @returns Whether watermark should be applied to generated documents
   */
  isWatermarkEnabled(): boolean {
    return !brandingAssets['watermark_disabled'].value;
  }

  /**
   * Get complete color scheme for document styling
   * @returns Object with primary, secondary, and accent colors
   */
  getFullColorScheme(): { 
    primary: string; 
    secondary: string; 
    accent: string; 
    background: string;
  } {
    return {
      primary: this.getColor('primary'),
      secondary: this.getColor('secondary'),
      accent: this.getColor('accent'),
      background: this.getColor('background')
    };
  }

  /**
   * Get complete branding configuration for document generation
   * @returns All branding elements needed for comprehensive document styling
   */
  getFullConfiguration(): {
    logos: Record<'primary' | 'secondary', string | null>;
    colors: Record<string, string>;
    fonts: Record<'body' | 'header', string>;
    watermarkEnabled: boolean;
  } {
    return {
      logos: {
        primary: this.getLogo('primary'),
        secondary: this.getLogo('secondary')
      },
      colors: {
        primary: this.getColor('primary'),
        secondary: this.getColor('secondary'),
        accent: this.getColor('accent'),
        background: this.getColor('background')
      },
      fonts: {
        body: this.getFont('body'),
        header: this.getFont('header')
      },
      watermarkEnabled: this.isWatermarkEnabled()
    };
  }
}

/**
 * Branding configuration singleton instance for use across document service
 */
const brandingAssetsInstance = new BrandingConfiguration();

export default brandingAssetsInstance;
export { brandingAssets, type BrandingAsset };
