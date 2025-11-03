"""Module for interacting with Microsoft Sentinel Content Hub and Solutions."""

import logging
import json
from typing import List, Dict, Any, Optional
from azure.mgmt.securityinsight import SecurityInsights
from azure.core.credentials import TokenCredential
from config import SentinelConfig

logger = logging.getLogger(__name__)


class ContentHubManager:
    """Manager for Sentinel Content Hub and Solutions."""
    
    def __init__(self, credential: TokenCredential, config: SentinelConfig):
        """Initialize the Content Hub manager.
        
        Args:
            credential: Azure credential for authentication.
            config: Sentinel configuration.
        """
        self.client = SecurityInsights(credential, config.subscription_id)
        self.config = config
    
    def list_installed_solutions(self) -> List[Dict[str, Any]]:
        """List all installed Sentinel solutions.
        
        Returns:
            List of installed solution details.
        """
        try:
            solutions = []
            # Note: This uses the content packages API
            package_list = self.client.content_packages.list(
                resource_group_name=self.config.resource_group,
                workspace_name=self.config.workspace_name
            )
            
            for package in package_list:
                solution_info = {
                    'id': package.id,
                    'name': package.name,
                    'type': package.type,
                    'kind': package.properties.content_kind if hasattr(package, 'properties') else 'Unknown',
                    'version': package.properties.version if hasattr(package, 'properties') else 'Unknown',
                    'display_name': package.properties.display_name if hasattr(package, 'properties') and hasattr(package.properties, 'display_name') else package.name,
                    'is_new': package.properties.is_new if hasattr(package, 'properties') and hasattr(package.properties, 'is_new') else False,
                    'is_featured': package.properties.is_featured if hasattr(package, 'properties') and hasattr(package.properties, 'is_featured') else False
                }
                
                solutions.append(solution_info)
            
            logger.info(f"Found {len(solutions)} installed solutions")
            return solutions
            
        except Exception as e:
            logger.error(f"Error listing installed solutions: {str(e)}")
            return []
    
    def get_available_content(self) -> List[Dict[str, Any]]:
        """Get available content from the Content Hub catalog.
        
        Returns:
            List of available content packages.
        """
        try:
            available_content = []
            
            # List available content from the catalog
            catalog_list = self.client.content_product_packages.list(
                resource_group_name=self.config.resource_group,
                workspace_name=self.config.workspace_name
            )
            
            for package in catalog_list:
                package_info = {
                    'id': package.id,
                    'name': package.name,
                    'package_id': package.properties.package_id if hasattr(package, 'properties') else 'Unknown',
                    'version': package.properties.version if hasattr(package, 'properties') else 'Unknown',
                    'display_name': package.properties.display_name if hasattr(package, 'properties') and hasattr(package.properties, 'display_name') else package.name,
                    'content_kind': package.properties.content_kind if hasattr(package, 'properties') else 'Unknown',
                    'publisher': package.properties.publisher_display_name if hasattr(package, 'properties') and hasattr(package.properties, 'publisher_display_name') else 'Unknown'
                }
                
                available_content.append(package_info)
            
            logger.info(f"Found {len(available_content)} available content packages")
            return available_content
            
        except Exception as e:
            logger.error(f"Error getting available content: {str(e)}")
            return []
    
    def check_solution_updates(self, installed_solutions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for updates to installed solutions.
        
        Args:
            installed_solutions: List of installed solutions.
            
        Returns:
            List of solutions with available updates.
        """
        updates_available = []
        available_content = self.get_available_content()
        
        # Create a lookup dictionary for available content
        available_lookup = {
            pkg['package_id']: pkg for pkg in available_content
        }
        
        for solution in installed_solutions:
            # Try to find matching available package
            solution_name = solution.get('name')
            current_version = solution.get('version', '0.0.0')
            
            # Look for matching package in available content
            for pkg_id, pkg in available_lookup.items():
                if solution_name in pkg_id or pkg['display_name'] == solution.get('display_name'):
                    available_version = pkg.get('version', '0.0.0')
                    
                    # Simple version comparison (you may want to use packaging.version for better comparison)
                    if self._compare_versions(current_version, available_version):
                        updates_available.append({
                            'solution_name': solution.get('display_name', solution_name),
                            'current_version': current_version,
                            'available_version': available_version,
                            'package_id': pkg_id,
                            'publisher': pkg.get('publisher', 'Unknown'),
                            'installed_id': solution['id']
                        })
                        break
        
        logger.info(f"Found {len(updates_available)} solutions with updates available")
        return updates_available
    
    def get_template_content(self, package_id: str) -> Optional[Dict[str, Any]]:
        """Get the template content for a specific package.
        
        Args:
            package_id: The package ID.
            
        Returns:
            Template content if available.
        """
        try:
            # Get the content product template
            template = self.client.content_product_templates.get(
                resource_group_name=self.config.resource_group,
                workspace_name=self.config.workspace_name,
                template_id=package_id
            )
            
            return {
                'id': template.id,
                'name': template.name,
                'content': template.properties.template_content if hasattr(template.properties, 'template_content') else None,
                'version': template.properties.version if hasattr(template.properties, 'version') else 'Unknown'
            }
            
        except Exception as e:
            logger.error(f"Error getting template content for {package_id}: {str(e)}")
            return None
    
    def _compare_versions(self, current: str, available: str) -> bool:
        """Compare two version strings.
        
        Args:
            current: Current version string.
            available: Available version string.
            
        Returns:
            True if available version is newer than current.
        """
        try:
            # Simple version comparison - split by '.' and compare
            current_parts = [int(x) for x in current.split('.') if x.isdigit()]
            available_parts = [int(x) for x in available.split('.') if x.isdigit()]
            
            # Pad shorter version with zeros
            max_len = max(len(current_parts), len(available_parts))
            current_parts.extend([0] * (max_len - len(current_parts)))
            available_parts.extend([0] * (max_len - len(available_parts)))
            
            return available_parts > current_parts
            
        except Exception as e:
            logger.warning(f"Error comparing versions {current} and {available}: {str(e)}")
            return False
    
    def get_rule_template(self, rule_template_id: str) -> Optional[Dict[str, Any]]:
        """Get analytic rule template details.
        
        Args:
            rule_template_id: The rule template ID.
            
        Returns:
            Rule template details.
        """
        try:
            template = self.client.alert_rule_templates.get(
                resource_group_name=self.config.resource_group,
                workspace_name=self.config.workspace_name,
                alert_rule_template_id=rule_template_id
            )
            
            return {
                'id': template.id,
                'name': template.name,
                'kind': template.kind if hasattr(template, 'kind') else 'Unknown',
                'properties': template.__dict__ if hasattr(template, '__dict__') else {}
            }
            
        except Exception as e:
            logger.error(f"Error getting rule template: {str(e)}")
            return None
    
    def list_rule_templates(self) -> List[Dict[str, Any]]:
        """List all available analytic rule templates.
        
        Returns:
            List of rule templates.
        """
        try:
            templates = []
            template_list = self.client.alert_rule_templates.list(
                resource_group_name=self.config.resource_group,
                workspace_name=self.config.workspace_name
            )
            
            for template in template_list:
                template_info = {
                    'id': template.id,
                    'name': template.name,
                    'kind': template.kind if hasattr(template, 'kind') else 'Unknown',
                    'display_name': template.display_name if hasattr(template, 'display_name') else template.name,
                    'severity': template.severity if hasattr(template, 'severity') else 'Unknown',
                    'tactics': template.tactics if hasattr(template, 'tactics') else [],
                    'required_data_connectors': template.required_data_connectors if hasattr(template, 'required_data_connectors') else []
                }
                
                templates.append(template_info)
            
            logger.info(f"Found {len(templates)} rule templates")
            return templates
            
        except Exception as e:
            logger.error(f"Error listing rule templates: {str(e)}")
            return []
