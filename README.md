# Efficient Shopping Optimizer 🛒

## Overview

This project is a data-driven attempt to optimize grocery purchases for individuals who are both health-conscious and budget-aware. As someone who deeply values efficiency in both time and spending, I wanted to explore how computational methods—particularly **optimization algorithms**—can help us make better decisions in our everyday lives.

## Objective

Build a simple but effective tool that helps users select the best combination of grocery items under a fixed budget, **maximizing nutritional value** while minimizing cost.  
The project reflects my own dietary goals: protein-focused, clean eating, with minimal reliance on processed snacks.

## Problem Definition

Many grocery shoppers struggle to balance nutrition with affordability. For someone following a specific meal plan, it's often unclear which combination of items gives the best value for money while meeting dietary goals.

This project formulates the problem as a **0-1 Knapsack Optimization Problem**:
- Each food item has:
  - a **cost** (price per unit),
  - a **value** (e.g. grams of protein),
  - and a **category** (protein, carb, vegetable, etc.).
- The goal is to **maximize total nutritional value** (e.g. total protein intake) while staying within a budget.

## My Role and Motivation

As someone driven by efficiency in both time and cost, I wanted to quantify and automate decisions I used to make intuitively. This project bridges my background in **mathematics, statistics, and data science** with my personal interest in health and finance.

## Optimization Focus

The model can be customized to optimize for different nutritional goals or combinations such as:
- **Protein per dollar** (primary focus)
- **Fiber per dollar**
- **Calories per dollar**
- Or a weighted scoring system (e.g. 70% protein, 30% fiber)

## Algorithm

The problem is solved using the **0-1 Knapsack algorithm**, which is suitable for binary decisions (either include the item or not).  
In future iterations, extensions like the **bounded knapsack** or **multi-objective optimization** can be applied.

## Next Steps

- Refine dataset (realistic prices, nutritional info, serving sizes)
- Implement optimization model
- Build UI or CLI to make the tool interactive

## File Structure
