"""
Interview Question Generator Workflow

This workflow combines CSV Filter Agent and Simple Agents to:
1. Fetch user profile from test-agent.csv
2. Generate interview questions based on user's profile using Ollama LLM
3. Return results in JSON format

Author: AI Assistant
Date: 2024-11-27
"""

import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.csv_filter_agent import CSVFilterAgent
from src.agents.simple_agents import SyncExecutorAgent


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InterviewQuestionWorkflow:
    """
    Workflow for generating interview questions based on user profiles.
    
    This workflow:
    1. Accepts user identifier (user_id or name)
    2. Fetches user profile from CSV using CSVFilterAgent
    3. Uses LLM agent to generate tailored interview questions
    4. Returns structured JSON response
    
    Example:
        ```python
        workflow = InterviewQuestionWorkflow(
            csv_file="test-agent.csv",
            data_dir="data/input"
        )
        
        result = workflow.generate_interview_questions(user_id=1)
        print(json.dumps(result, indent=2))
        ```
    """
    
    def __init__(
        self,
        csv_file: str = "test-agent.csv",
        data_dir: str = "data/input",
        llm_provider: str = "ollama",
        llm_model: str = "llama3.2",
        num_questions: int = 5
    ):
        """
        Initialize the workflow.
        
        Args:
            csv_file: Name of the CSV file containing user profiles
            data_dir: Directory containing the CSV file
            llm_provider: LLM provider to use (ollama, openai)
            llm_model: Model name
            num_questions: Number of interview questions to generate
        """
        self.csv_file = csv_file
        self.data_dir = data_dir
        self.num_questions = num_questions
        
        # Initialize CSV Filter Agent
        self.csv_agent = CSVFilterAgent(data_dir=data_dir)
        logger.info(f"Initialized CSV Filter Agent with data_dir: {data_dir}")
        
        # Initialize LLM Agent for question generation
        system_prompt = """You are an expert technical interviewer. Your role is to:
- Generate relevant, insightful interview questions based on candidate profiles
- Tailor questions to the candidate's skills, experience, and job role
- Create questions that assess both technical knowledge and problem-solving abilities
- Provide a mix of theoretical and practical questions
- Consider the candidate's experience level when formulating questions

Return your response ONLY as a valid JSON object with the following structure:
{
    "questions": [
        {
            "question": "Question text here",
            "category": "Technical/Behavioral/Problem-Solving",
            "difficulty": "Easy/Medium/Hard",
            "focus_area": "Specific skill or topic"
        }
    ]
}

Do NOT include any text before or after the JSON object."""
        
        self.llm_agent = SyncExecutorAgent(
            system_prompt=system_prompt,
            llm_provider=llm_provider,
            llm_model=llm_model
        )
        logger.info(f"Initialized LLM Agent: {llm_provider}/{llm_model}")
    
    def fetch_user_profile(
        self,
        user_id: Optional[int] = None,
        name: Optional[str] = None,
        active_only: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch user profile from CSV.
        
        Args:
            user_id: User ID to search for
            name: User name to search for
            active_only: Only return active users
            
        Returns:
            User profile dictionary
            
        Raises:
            ValueError: If no matching user found or multiple users found
        """
        logger.info(f"Fetching user profile: user_id={user_id}, name={name}")
        
        # Determine search criteria
        if user_id is not None:
            filter_column = "user_id"
            filter_value = user_id
        elif name is not None:
            filter_column = "name"
            filter_value = name
        else:
            raise ValueError("Either user_id or name must be provided")
        
        # Fetch user from CSV
        try:
            input_data = {
                "csv_file_name": self.csv_file,
                "filtered_column_name": filter_column,
                "value": filter_value
            }
            
            users = self.csv_agent.process(input_data)
            
            if not users:
                raise ValueError(f"No user found with {filter_column}={filter_value}")
            
            # Filter for active users if required
            if active_only:
                users = [u for u in users if u.get("active", False)]
                if not users:
                    raise ValueError(f"No active user found with {filter_column}={filter_value}")
            
            if len(users) > 1:
                logger.warning(f"Multiple users found, using first match")
            
            user_profile = users[0]
            logger.info(f"Found user: {user_profile.get('name', 'Unknown')}")
            
            return user_profile
        
        except Exception as e:
            logger.error(f"Error fetching user profile: {e}")
            raise
    
    def _build_question_prompt(self, user_profile: Dict[str, Any]) -> str:
        """
        Build the prompt for generating interview questions.
        
        Args:
            user_profile: User profile dictionary
            
        Returns:
            Formatted prompt string
        """
        # Extract profile information
        name = user_profile.get("name", "Unknown")
        skills = user_profile.get("skills", "Not specified")
        experience = user_profile.get("experience_years", "Unknown")
        job_role = user_profile.get("job_role", "Not specified")
        
        prompt = f"""Generate {self.num_questions} interview questions for the following candidate profile:

Candidate Name: {name}
Job Role: {job_role}
Skills: {skills}
Years of Experience: {experience}

Generate questions that:
1. Are relevant to their skills and experience level
2. Cover different aspects of their expertise
3. Include a mix of technical, behavioral, and problem-solving questions
4. Are appropriate for their experience level ({experience} years)

Return ONLY a JSON object with the structure specified in your instructions. No additional text."""
        
        return prompt
    
    def generate_interview_questions(
        self,
        user_id: Optional[int] = None,
        name: Optional[str] = None,
        active_only: bool = True
    ) -> Dict[str, Any]:
        """
        Generate interview questions for a user.
        
        Args:
            user_id: User ID to generate questions for
            name: User name to generate questions for
            active_only: Only process active users
            
        Returns:
            Dictionary with user profile and generated questions
            
        Example:
            ```python
            result = workflow.generate_interview_questions(user_id=1)
            print(json.dumps(result, indent=2))
            ```
        """
        try:
            # Step 1: Fetch user profile
            logger.info("Step 1: Fetching user profile...")
            user_profile = self.fetch_user_profile(
                user_id=user_id,
                name=name,
                active_only=active_only
            )
            
            # Step 2: Build prompt for LLM
            logger.info("Step 2: Building question generation prompt...")
            prompt = self._build_question_prompt(user_profile)
            
            # Step 3: Generate questions using LLM
            logger.info("Step 3: Generating interview questions with LLM...")
            llm_response = self.llm_agent.execute_sync(prompt)
            
            # Step 4: Parse LLM response
            logger.info("Step 4: Parsing LLM response...")
            try:
                # Try to extract JSON from response
                response_text = llm_response.strip()
                
                # Remove markdown code blocks if present
                if response_text.startswith("```"):
                    lines = response_text.split("\n")
                    response_text = "\n".join(lines[1:-1])
                
                questions_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                logger.debug(f"LLM Response: {llm_response}")
                
                # Fallback: wrap response in a structure
                questions_data = {
                    "questions": [
                        {
                            "question": llm_response,
                            "category": "General",
                            "difficulty": "Medium",
                            "focus_area": "Mixed"
                        }
                    ],
                    "parse_error": True
                }
            
            # Step 5: Build final response
            logger.info("Step 5: Building final response...")
            result = {
                "status": "success",
                "user_profile": {
                    "user_id": user_profile.get("user_id"),
                    "name": user_profile.get("name"),
                    "job_role": user_profile.get("job_role"),
                    "skills": user_profile.get("skills"),
                    "experience_years": user_profile.get("experience_years"),
                    "active": user_profile.get("active")
                },
                "interview_questions": questions_data.get("questions", []),
                "metadata": {
                    "total_questions": len(questions_data.get("questions", [])),
                    "requested_questions": self.num_questions,
                    "llm_provider": self.llm_agent.llm_provider_name,
                    "llm_model": self.llm_agent.llm_model_name
                }
            }
            
            logger.info("Interview questions generated successfully")
            return result
        
        except Exception as e:
            logger.error(f"Error in workflow: {e}")
            return {
                "status": "error",
                "error": str(e),
                "user_profile": None,
                "interview_questions": []
            }
    
    def generate_questions_batch(
        self,
        user_ids: Optional[List[int]] = None,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Generate interview questions for multiple users.
        
        Args:
            user_ids: List of user IDs (None = all users)
            active_only: Only process active users
            
        Returns:
            List of results for each user
            
        Example:
            ```python
            results = workflow.generate_questions_batch(user_ids=[1, 2, 3])
            for result in results:
                print(json.dumps(result, indent=2))
            ```
        """
        logger.info(f"Starting batch generation for {len(user_ids) if user_ids else 'all'} users")
        
        # If no user_ids provided, fetch all users
        if user_ids is None:
            # Get all active users
            try:
                input_data = {
                    "csv_file_name": self.csv_file,
                    "filtered_column_name": "active",
                    "value": True
                }
                users = self.csv_agent.process(input_data)
                user_ids = [u.get("user_id") for u in users]
                logger.info(f"Found {len(user_ids)} active users")
            except Exception as e:
                logger.error(f"Error fetching users: {e}")
                return []
        
        # Generate questions for each user
        results = []
        for user_id in user_ids:
            logger.info(f"Processing user_id: {user_id}")
            result = self.generate_interview_questions(
                user_id=user_id,
                active_only=active_only
            )
            results.append(result)
        
        logger.info(f"Batch generation completed: {len(results)} results")
        return results


def main():
    """Example usage of the workflow"""
    print("\n" + "="*80)
    print("INTERVIEW QUESTION GENERATOR WORKFLOW")
    print("="*80 + "\n")
    
    # Initialize workflow
    workflow = InterviewQuestionWorkflow(
        csv_file="test-agent.csv",
        data_dir="data/input",
        llm_provider="ollama",
        llm_model="llama3.2",
        num_questions=5
    )
    
    # Example 1: Generate questions for specific user
    print("\n" + "-"*80)
    print("Example 1: Generate questions for user_id=1")
    print("-"*80)
    
    result = workflow.generate_interview_questions(user_id=1)
    print(json.dumps(result, indent=2))
    
    # Example 2: Generate questions by name
    print("\n" + "-"*80)
    print("Example 2: Generate questions for 'Jane Smith'")
    print("-"*80)
    
    result = workflow.generate_interview_questions(name="Jane Smith")
    print(json.dumps(result, indent=2))
    
    # Example 3: Batch generation
    print("\n" + "-"*80)
    print("Example 3: Batch generation for multiple users")
    print("-"*80)
    
    results = workflow.generate_questions_batch(user_ids=[1, 2])
    print(f"Generated questions for {len(results)} users")
    for i, result in enumerate(results, 1):
        print(f"\nUser {i}: {result['user_profile']['name']}")
        print(f"Questions: {result['metadata']['total_questions']}")
    
    print("\n" + "="*80)
    print("WORKFLOW COMPLETED")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
