addMemories的返回消息实例：
```json
{
  "results": [
    {
      "id": "4e737279-653f-4395-858f-7e1385c7444a",
      "memory": "Likes to eat pizza",
      "event": "ADD",
      "categories": [
        "food"
      ]
    },
    {
      "id": "8e531993-d958-4e4d-9d2c-bdeacb02b6d3",
      "memory": "Has a dog named Pitter",
      "event": "ADD",
      "categories": [
        "family",
        "misc"
      ]
    }
  ],
  "relations": {
    "deleted_relations": [],
    "added_triples": [
      [
        {
          "source": "morethan",
          "source_labels": [
            "person"
          ],
          "relationship": "likes_to_eat",
          "target": "pizza",
          "target_labels": [
            "food"
          ]
        }
      ],
      [
        {
          "source": "morethan",
          "source_labels": [
            "person"
          ],
          "relationship": "has_a_dog_named",
          "target": "pitter",
          "target_labels": [
            "pet",
            "dog"
          ]
        }
      ]
    ]
  }
}
```

searchInternalMemories返回的消息
```json
{
  "results": [
    {
      "id": "900a0743-2848-4f7b-be63-877febec2ace",
      "memory": "Likes to eat pizza",
      "hash": "e0b64254f555327eca2f7fd606dbb680",
      "metadata": null,
      "score": 0.7150987,
      "created_at": "2025-02-27T04:16:43.555340-08:00",
      "updated_at": null,
      "categories": [
        "food"
      ],
      "user_id": "morethan"
    },
    {
      "id": "7218a4dc-f0fb-4694-a049-2d3169d09c28",
      "memory": "Has a dog named Pitter",
      "hash": "92109e7b859ba4f008cc653443676f3a",
      "metadata": null,
      "score": 0.45113054,
      "created_at": "2025-02-27T04:16:43.773530-08:00",
      "updated_at": null,
      "categories": [
        "family",
        "hobbies"
      ],
      "user_id": "morethan"
    }
  ],
  "relations": [
    {
      "source": "morethan",
      "relationship": "likes_to_eat",
      "destination": "pizza"
    },
    {
      "source": "morethan",
      "relationship": "has_a_dog_named",
      "destination": "pitter"
    }
  ]
}
```