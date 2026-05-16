"""
Initialize database with mock data for development and testing.
"""
import asyncio
from utils.database import init_db, get_db
from mock_data.fixtures import MockDataGenerator
from models.deployment import Deployment
from models.workflow import Workflow, WorkflowStep
from utils.logger import setup_logging, get_logger

logger = get_logger(__name__)


async def populate_mock_data():
    """Populate database with mock data."""
    logger.info("Generating mock data...")
    
    # Generate sample data
    sample_data = MockDataGenerator.generate_sample_data()
    
    async for session in get_db():
        try:
            # Add deployments
            logger.info(f"Adding {len(sample_data['deployments'])} deployments...")
            for deployment in sample_data['deployments']:
                session.add(deployment)
            
            # Add workflows
            logger.info(f"Adding {len(sample_data['workflows'])} workflows...")
            for workflow in sample_data['workflows']:
                session.add(workflow)
            
            # Add workflow steps
            logger.info(f"Adding {len(sample_data['workflow_steps'])} workflow steps...")
            for step in sample_data['workflow_steps']:
                session.add(step)
            
            # Commit all changes
            await session.commit()
            logger.info("Mock data populated successfully!")
            
            # Print summary
            logger.info("\n=== Mock Data Summary ===")
            logger.info(f"Deployments: {len(sample_data['deployments'])}")
            logger.info(f"Workflows: {len(sample_data['workflows'])}")
            logger.info(f"Workflow Steps: {len(sample_data['workflow_steps'])}")
            logger.info("========================\n")
            
        except Exception as e:
            logger.error(f"Error populating mock data: {e}")
            await session.rollback()
            raise
        finally:
            break  # Exit after first iteration


async def main():
    """Main function to initialize database and populate mock data."""
    setup_logging()
    logger.info("Starting database initialization...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized successfully!")
    
    # Populate mock data
    await populate_mock_data()
    
    logger.info("Database setup complete! You can now start the backend server.")


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
