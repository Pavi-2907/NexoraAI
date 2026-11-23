
import os
import json
import re
from datetime import datetime
from dotenv import load_dotenv
from groq import AsyncGroq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError("GROQ_API_KEY is not configured.")

client = AsyncGroq(api_key=api_key)

MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b",
)

CLASSIFIER_MODEL = "openai/gpt-oss-20b"


async def needs_web_search(question: str) -> bool:
    """Determine whether a question requires web search."""

    completion = await client.chat.completions.create(
        model=CLASSIFIER_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a search requirement classifier. "
                    "Determine whether the user's question requires "
                    "current, recent, live, or externally updated information. "
                    "Return true if web search is necessary. "
                    "Return false if the question can be answered using "
                    "general knowledge or reasoning. "
                    'Respond only with JSON: {"needs_search": true} '
                    'or {"needs_search": false}.'
                ),
            },
            {
                "role": "user",
                "content": question,
            },
        ],
        response_format={"type": "json_object"},
    )

    result = completion.choices[0].message.content

    try:
        classification = json.loads(result)

        if not isinstance(classification, dict):
            raise ValueError("Classifier response must be a JSON object.")

        needs_search = classification.get("needs_search")

        if not isinstance(needs_search, bool):
            raise ValueError("Invalid needs_search value in classifier response.")

        return needs_search

    except (json.JSONDecodeError, TypeError, ValueError):
        raise RuntimeError("Unable to classify the search requirement.")

    

CURRENT_YEAR = datetime.now().year


async def generate_response(question: str) -> dict:
    """Generate a response with web search when required."""

    search_required = await needs_web_search(question)

    completion = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are NexoraAI, a helpful, reliable, and knowledgeable AI assistant. "

                    "GENERAL RESPONSE GUIDELINES: "
                    "Understand the user's intent before answering. "
                    "Provide clear, accurate, relevant, and well-structured responses. "
                    "Adapt explanations to the user's question and required level of detail. "
                    "Avoid unnecessary information, repetition, and unsupported claims. "
                    "Never invent facts or pretend to know something you cannot verify. "

                    "WEB SEARCH GUIDELINES: "
                    "When web search is available and relevant: "
                    "Search for information that directly answers the user's question. "

                    "SEARCH QUERY INSTRUCTIONS: "
                    "For latest or current developments: "
                    f"Always prioritize the current year ({CURRENT_YEAR}) in search queries. "
                    "Never add previous years such as 2024 or 2025 unless explicitly requested. "
                    "Do not search for historical model releases as current developments. "
                    "Search for recent announcements, papers, releases and updates. "

                    "INFORMATION FRESHNESS AND QUALITY: "
                    "For questions about latest developments, current events, recent updates, "
                    "trends, releases, or versions, prioritize the most recent available information. "
                    "Verify publication dates and distinguish the date an event occurred "
                    "from the date an article was published. "
                    "Prefer reliable sources, including official announcements, "
                    "technical documentation, research publications, and reputable news organizations. "
                    "Use older sources only when historical background or context is necessary. "
                    "Exclude irrelevant, duplicate, outdated, or weakly supported information. "
                    "Cross-check important claims using multiple reliable sources when appropriate. "
                    "Never present historical information as a recent development. "
                    "If sufficiently recent information cannot be found, clearly communicate that limitation. "
                    "Include relevant source URLs when available. "

                    "CITATION AND EVIDENCE RULES: "
                    "Support important factual claims with citations from retrieved search results. "
                    "Use citations only when the source directly supports the associated claim. "
                    "Prefer primary sources such as official announcements, research papers, "
                    "and technical documentation for technical claims and specifications. "
                    "Never invent citations, source references, or URLs. "
                    "If a claim cannot be verified using available sources, "
                    "clearly communicate the uncertainty instead of presenting it as a confirmed fact. "

                    "ANSWER GENERATION: "
                    "Organize information logically. "
                    "Explain important developments and why they matter. "
                    "Distinguish verified facts from uncertainty. "
                    "Keep the response focused on the user's actual question. "
                    "Do not claim that information is current unless the available evidence supports it."
                ),
            },
            {
                "role": "user",
                "content": question,
            },
        ],
        citation_options="disabled",
        tools=[{"type": "browser_search"}] if search_required else [],
        tool_choice="auto" if search_required else "none",
    )

    message = completion.choices[0].message
    answer = re.sub(
        r"【\d+†L\d+(?:-L\d+)?】",
        "",
        message.content or "",
    ).strip()

    # Collect and merge source information.
    sources_by_url = {}

    for tool in message.executed_tools or []:
        tool_data = tool.model_dump()

        search_results = tool_data.get("search_results") or {}

        for result in search_results.get("results") or []:
            title = result.get("title")
            url = result.get("url")
            content = result.get("content") or ""

            if not url:
                continue

            # Identify browser metadata titles.
            is_metadata = (
                not title or "viewing lines" in title.lower()
            )

            # Create a record even when the title is metadata.
            if url not in sources_by_url:
                sources_by_url[url] = {
                    "title": None if is_metadata else title,
                    "url": url,
                    "content": "",
                }

            # Replace a metadata title with a proper title when available.
            elif not is_metadata and (
                not sources_by_url[url]["title"]
            ):
                sources_by_url[url]["title"] = title

            # Keep the most detailed available webpage content.
            if len(content) > len(sources_by_url[url]["content"]):
                sources_by_url[url]["content"] = content

    # Return only sources with retrieved webpage content.
    # Keep webpage content internal.
    sources = [
        {
            "title": source["title"] or source["url"],
            "url": source["url"],
        }
        for source in sources_by_url.values()
        if source["content"].strip()
    ]

    return {
        "answer": answer or "",
        "sources": sources,
    }
