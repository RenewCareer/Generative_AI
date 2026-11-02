# Module 05: Multimodal AI

**Slides:** [presentation.pptx](presentation.pptx) | **Time:** 3 hours | **Next:** [Module 06](../06_Backend%20Application%20interfaces/README.md)

## Learning outcomes

By the end, students can:

- Send images to a model, and get validated data back
- Generate images with a structured prompt
- Build a speech pipeline in both directions
- Route work to the cheapest modality that does the job

## Session plan

| Time | Activity | Material |
|---|---|---|
| 15 min | Slides | `presentation.pptx` |
| 30 min | Images as input | `lessons/01_image_as_input.py`, `project/media.py` |
| 20 min | Image generation | `lessons/02_image_generation.py` |
| 25 min | Voice | `lessons/03_voice_pipeline.py` |
| 20 min | Routing a real PDF | `lessons/04_document_vision_routing.py` |
| 30 min | Example app | `project/expense_assistant.py` |
| 40 min | Lab | Below |

## Concepts

**Same patterns, new inputs.** Schemas, validation and evaluation stay the same when the input is an image.

**Images in requests.** An image is usually sent as base64 data, a hosted URL, or a file ID. Resize first, because
large photos cost more, and rarely help. Providers charge for images in tokens, so check their pricing.

**The model reads, code decides.** This is the most important design rule here:

| The model | Your code |
|---|---|
| Reads messy, varied photos | Checks that the items add up |
| Understands unseen layouts | Applies policy, such as removing alcohol |
| May misread a blurry digit | Gives the same result every time |

If the items do not add up, the receipt goes to a person. That one check catches many misreads.

**Images can carry injections.** Text inside a picture is also text the model reads. The extraction prompt
says that it is data.

**Voice** chains speech-to-text, a normal LLM app, and text-to-speech, and the caller feels every delay. Stream at
each stage. Realtime speech-to-speech APIs reduce latency, with less control over each stage. Spoken replies need
their own short style. Tell callers that they are talking to an AI, and get consent to record.

**Routing.** Vision calls cost more than text. Check each page, and use the cheapest method that works.

**Provider differences.** Check current documentation, as these change quickly. At the time of writing, the course
code uses OpenAI for vision, images and speech. Claude accepts images as input, and in this code it uses a labelled
placeholder for image generation, and the mock for speech.

## Run it

```powershell
python lessons/01_image_as_input.py
python lessons/02_image_generation.py
python lessons/03_voice_pipeline.py
python lessons/04_document_vision_routing.py
python project/expense_assistant.py
python -m pytest tests
```

**What is simulated offline.** Be open about this with students:

| Feature | Offline behaviour |
|---|---|
| Receipt reading | Reads a sidecar file with the true values, not the image |
| Image generation | Draws a placeholder labelled "NOT AI GENERATED" |
| Transcription | Returns a simulated transcript, labelled as mock |
| Speech | Writes a tone, not speech |

Model names are set in `.env`, because they change often. Check them against your provider's current list.

### What to expect

```
Merchant: Harbour Bistro (meal), total 45.00 USD
  - Grilled fish: 24.50
  - Salad: 9.00
  - Glass of wine: 8.50
  - Sparkling water: 3.00

Decision: APPROVE, reimbursable 36.50
  - Removed 8.50 of alcohol, which is not reimbursable.
```

From the routing lesson, on the 48-page NIST PDF:

```
  text            42 pages
  text+vision      4 pages
  vision           1 pages
  skip             1 pages
```

## A real bug to discuss

The first routing version sent 46 of 48 pages to vision. Every page in this PDF has an invisible full-page background
shape, and the code counted that as a figure. The unit tests passed, because they tested the rules, and not real pages.
Printing measurements for real pages found it. Two lessons: check heuristics on real data, and add a test that uses
real data (`test_vision_routing_on_the_real_pdf_sends_most_pages_to_text`). The current version only counts raster images,
so it misses figures drawn as vector graphics, and the code says so.

## Code walkthrough

| Part | Teaching point |
|---|---|
| `media.encode_image` | Resizes before encoding |
| `media.extract_from_image` | One function, with a branch per provider |
| `expense_assistant.Receipt` | Optional fields allow "unreadable", rather than a guess |
| `expense_assistant.apply_policy` | No model involved: exact, auditable, unit-tested |
| `tests/test_multimodal.py` | Tests real SDK requests against fake HTTP servers |

## Industry standards

- Evaluate on real inputs: blurry photos, odd angles, other languages
- Human review for uncertain or high-stakes results
- Rights and consent for images and voices
- Label synthetic media where required, for example under the EU AI Act's transparency rules
- Protect sensitive data: images often contain faces, IDs and card numbers

## Lab

1. Draw a receipt where the items do not add up, and confirm that it is flagged for review.
2. Add a `transport` category with its own limit and rule.
3. Dictate a claim note, transcribe it, and attach it to the decision.

**Marking notes.** Task 1 is fully offline: edit the data in `make_sample_receipt`. Task 2: add to `LIMITS`, with tests at the
limit and over it. Task 3 needs a key for real transcription. Offline, students can use the mock to build the plumbing.

**Stretch:** find the smallest image size at which a real receipt still extracts correctly.

## Check for understanding

1. Why not let the model apply the expense policy? *Policy must be exact, repeatable and auditable.*
2. Why resize images? *To reduce cost and latency, usually with no loss of quality.*
3. How does the app catch a misread digit? *It compares the sum of the items to the total.*
4. Why can text in an image be a security risk? *The model reads it, so it can contain injected instructions.*
