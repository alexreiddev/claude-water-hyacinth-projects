package com.expensetracker.domain.repository

import com.expensetracker.domain.model.Category
import com.expensetracker.domain.model.Expense
import kotlinx.coroutines.flow.Flow

interface ExpenseRepository {
    fun getAll(): Flow<List<Expense>>

    suspend fun getById(id: Long): Expense?

    suspend fun save(expense: Expense): Long

    suspend fun delete(id: Long)

    fun getByCategory(category: Category): Flow<List<Expense>>

    suspend fun searchByDescription(query: String): List<Expense>
}
