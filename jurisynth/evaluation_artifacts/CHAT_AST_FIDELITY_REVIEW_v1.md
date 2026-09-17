# AST intent-fidelity review

This is a successful compilation/first-leaf interpretation component smoke, not proof of complete query coverage or end-to-end legal QA. Review whether the AST preserves every distinct original request, scenario facts, uncertainty and conditional scope. Specifically check GDPR data reuse, cross-regime compliance, subgroup performance and incident-response questions. For each dependency, distinguish a real need for an upstream answer from a related topic. Do not force dependencies merely to make the tree look complex. Return omissions, unsupported additions, questionable edges, and a proposed faithful decomposition. Changes to prompts/planning require owner approval. No legal answer is requested.

## Original user question

m a bit confused about how all of this is supposed to work in practice. Say a hospital in the EU is using an AI medical system made by a company outside the EU, but it’s being sold through an EU importer/distributor, and the system is used to help doctors decide on treatments. It also processes patient health data and maybe biometric data, and the model keeps getting updated after deployment.

What I’m trying to figure out is: who is actually responsible for what here? Like, is the non-EU company automatically the provider, does the importer take on some of those responsibilities, and can the hospital itself somehow become the provider if it modifies the system or fine-tunes it later? Also, does the fact that it’s a medical device automatically make it high-risk under the AI Act, or are there extra conditions?

I’m also not sure how this overlaps with GDPR. If the hospital or company reuses patient data to improve the model, is that allowed just because they’re already processing the data for healthcare? And does complying with the AI Act make the GDPR side okay too, or are those completely separate things?

Then suppose there’s a software update and the system suddenly starts performing worse for one group of patients, but it’s not immediately obvious whether that counts as a serious incident or just a performance problem. Who is supposed to notice this first, who has to report it, and who is responsible for fixing or withdrawing the system?

Please work through this step by step, and if different EU laws seem to overlap or point in slightly different directions, don’t just smooth it over. I’d rather know where the uncertainty or conflict actually is.


## Preserved compilation

```json
{
  "expression": "(Under the EU AI Act, who qualifies as the 'provider' of a high-risk AI system that is a medical device when the manufacturer is established outside the EU, the system is placed on the market via an EU importer/distributor, and the hospital (deployer) may modify or fine-tune the system after deployment? * (Using {upstream_result}, Does the AI Act automatically classify an AI system that is a medical device (or an accessory/safety component of one) as high-risk, or are there additional conditions (e.g., specific risk class under MDR/IVDR, intended purpose, Annex III listing) that must be met? + Using {upstream_result}, How are provider obligations (conformity assessment, quality management system, technical documentation, post-market monitoring, incident reporting, registration) allocated between the non-EU manufacturer, the EU authorised representative, the importer, and the distributor under the AI Act when the system is a medical device? + Using {upstream_result}, Under what circumstances does a deployer (hospital) become a 'provider' under the AI Act by substantially modifying the intended purpose or making a substantial modification to a high-risk AI system, and what specific actions (e.g., fine-tuning, retraining, changing clinical workflow integration) trigger this change of status?))",
  "ast": {
    "type": "ListQuery",
    "query": "(Under the EU AI Act, who qualifies as the 'provider' of a high-risk AI system that is a medical device when the manufacturer is established outside the EU, the system is placed on the market via an EU importer/distributor, and the hospital (deployer) may modify or fine-tune the system after deployment? * (Using {upstream_result}, Does the AI Act automatically classify an AI system that is a medical device (or an accessory/safety component of one) as high-risk, or are there additional conditions (e.g., specific risk class under MDR/IVDR, intended purpose, Annex III listing) that must be met? + Using {upstream_result}, How are provider obligations (conformity assessment, quality management system, technical documentation, post-market monitoring, incident reporting, registration) allocated between the non-EU manufacturer, the EU authorised representative, the importer, and the distributor under the AI Act when the system is a medical device? + Using {upstream_result}, Under what circumstances does a deployer (hospital) become a 'provider' under the AI Act by substantially modifying the intended purpose or making a substantial modification to a high-risk AI system, and what specific actions (e.g., fine-tuning, retraining, changing clinical workflow integration) trigger this change of status?))",
    "children": [
      {
        "type": "ListQuery",
        "query": "(Under the EU AI Act, who qualifies as the 'provider' of a high-risk AI system that is a medical device when the manufacturer is established outside the EU, the system is placed on the market via an EU importer/distributor, and the hospital (deployer) may modify or fine-tune the system after deployment? * (Using {upstream_result}, Does the AI Act automatically classify an AI system that is a medical device (or an accessory/safety component of one) as high-risk, or are there additional conditions (e.g., specific risk class under MDR/IVDR, intended purpose, Annex III listing) that must be met? + Using {upstream_result}, How are provider obligations (conformity assessment, quality management system, technical documentation, post-market monitoring, incident reporting, registration) allocated between the non-EU manufacturer, the EU authorised representative, the importer, and the distributor under the AI Act when the system is a medical device? + Using {upstream_result}, Under what circumstances does a deployer (hospital) become a 'provider' under the AI Act by substantially modifying the intended purpose or making a substantial modification to a high-risk AI system, and what specific actions (e.g., fine-tuning, retraining, changing clinical workflow integration) trigger this change of status?))",
        "children": [
          {
            "type": "DependentQuery",
            "query": "Under the EU AI Act, who qualifies as the 'provider' of a high-risk AI system that is a medical device when the manufacturer is established outside the EU, the system is placed on the market via an EU importer/distributor, and the hospital (deployer) may modify or fine-tune the system after deployment? * (Using {upstream_result}, Does the AI Act automatically classify an AI system that is a medical device (or an accessory/safety component of one) as high-risk, or are there additional conditions (e.g., specific risk class under MDR/IVDR, intended purpose, Annex III listing) that must be met? + Using {upstream_result}, How are provider obligations (conformity assessment, quality management system, technical documentation, post-market monitoring, incident reporting, registration) allocated between the non-EU manufacturer, the EU authorised representative, the importer, and the distributor under the AI Act when the system is a medical device? + Using {upstream_result}, Under what circumstances does a deployer (hospital) become a 'provider' under the AI Act by substantially modifying the intended purpose or making a substantial modification to a high-risk AI system, and what specific actions (e.g., fine-tuning, retraining, changing clinical workflow integration) trigger this change of status?)",
            "children": [
              {
                "type": "AtomicQuery",
                "query": "Under the EU AI Act, who qualifies as the 'provider' of a high-risk AI system that is a medical device when the manufacturer is established outside the EU, the system is placed on the market via an EU importer/distributor, and the hospital (deployer) may modify or fine-tune the system after deployment?",
                "children": []
              },
              {
                "type": "ListQuery",
                "query": "(Using {upstream_result}, Does the AI Act automatically classify an AI system that is a medical device (or an accessory/safety component of one) as high-risk, or are there additional conditions (e.g., specific risk class under MDR/IVDR, intended purpose, Annex III listing) that must be met? + Using {upstream_result}, How are provider obligations (conformity assessment, quality management system, technical documentation, post-market monitoring, incident reporting, registration) allocated between the non-EU manufacturer, the EU authorised representative, the importer, and the distributor under the AI Act when the system is a medical device? + Using {upstream_result}, Under what circumstances does a deployer (hospital) become a 'provider' under the AI Act by substantially modifying the intended purpose or making a substantial modification to a high-risk AI system, and what specific actions (e.g., fine-tuning, retraining, changing clinical workflow integration) trigger this change of status?)",
                "children": [
                  {
                    "type": "AtomicQuery",
                    "query": "Using {upstream_result}, Does the AI Act automatically classify an AI system that is a medical device (or an accessory/safety component of one) as high-risk, or are there additional conditions (e.g., specific risk class under MDR/IVDR, intended purpose, Annex III listing) that must be met?",
                    "children": []
                  },
                  {
                    "type": "AtomicQuery",
                    "query": "Using {upstream_result}, How are provider obligations (conformity assessment, quality management system, technical documentation, post-market monitoring, incident reporting, registration) allocated between the non-EU manufacturer, the EU authorised representative, the importer, and the distributor under the AI Act when the system is a medical device?",
                    "children": []
                  },
                  {
                    "type": "AtomicQuery",
                    "query": "Using {upstream_result}, Under what circumstances does a deployer (hospital) become a 'provider' under the AI Act by substantially modifying the intended purpose or making a substantial modification to a high-risk AI system, and what specific actions (e.g., fine-tuning, retraining, changing clinical workflow integration) trigger this change of status?",
                    "children": []
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  },
  "leaves": [
    {
      "query_id": "q001",
      "query": "Under the EU AI Act, who qualifies as the 'provider' of a high-risk AI system that is a medical device when the manufacturer is established outside the EU, the system is placed on the market via an EU importer/distributor, and the hospital (deployer) may modify or fine-tune the system after deployment?",
      "dependency_ids": [],
      "contextual_facts": [],
      "constraints": {},
      "optional_dependency_ids": []
    },
    {
      "query_id": "q002",
      "query": "Using {upstream_result}, Does the AI Act automatically classify an AI system that is a medical device (or an accessory/safety component of one) as high-risk, or are there additional conditions (e.g., specific risk class under MDR/IVDR, intended purpose, Annex III listing) that must be met?",
      "dependency_ids": [
        "q001"
      ],
      "contextual_facts": [],
      "constraints": {
        "qcompiler_placeholders": [
          "upstream_result"
        ]
      },
      "optional_dependency_ids": []
    },
    {
      "query_id": "q003",
      "query": "Using {upstream_result}, How are provider obligations (conformity assessment, quality management system, technical documentation, post-market monitoring, incident reporting, registration) allocated between the non-EU manufacturer, the EU authorised representative, the importer, and the distributor under the AI Act when the system is a medical device?",
      "dependency_ids": [
        "q001"
      ],
      "contextual_facts": [],
      "constraints": {
        "qcompiler_placeholders": [
          "upstream_result"
        ]
      },
      "optional_dependency_ids": []
    },
    {
      "query_id": "q004",
      "query": "Using {upstream_result}, Under what circumstances does a deployer (hospital) become a 'provider' under the AI Act by substantially modifying the intended purpose or making a substantial modification to a high-risk AI system, and what specific actions (e.g., fine-tuning, retraining, changing clinical workflow integration) trigger this change of status?",
      "dependency_ids": [
        "q001"
      ],
      "contextual_facts": [],
      "constraints": {
        "qcompiler_placeholders": [
          "upstream_result"
        ]
      },
      "optional_dependency_ids": []
    }
  ],
  "attempts": 1
}
```
