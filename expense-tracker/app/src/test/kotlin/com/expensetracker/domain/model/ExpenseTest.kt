package com.expensetracker.domain.model

import java.math.BigDecimal
import java.time.Instant
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class ExpenseTest {
    @Test
    fun `expense has correct default tag list`() {
        val expense =
            Expense(
                amount = BigDecimal("42.50"),
                description = "Lunch",
                category = Category.FOOD,
                source = IngestionSource.MANUAL,
                timestamp = Instant.now(),
            )
        assertTrue(expense.tags.isEmpty())
    }

    @Test
    fun `expense preserves all assigned tags`() {
        val tags = listOf("work", "reimbursable")
        val expense =
            Expense(
                amount = BigDecimal("15.00"),
                description = "Coffee meeting",
                category = Category.FOOD,
                tags = tags,
                source = IngestionSource.MANUAL,
                timestamp = Instant.now(),
            )
        assertEquals(tags, expense.tags)
    }
}
