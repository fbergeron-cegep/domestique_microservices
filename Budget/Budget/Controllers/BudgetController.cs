
using System.Collections.Generic;
using Microsoft.AspNetCore.Mvc;
using MySqlConnector;

namespace Budget.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class BudgetController : ControllerBase
    {
        private readonly MySqlConnection _connection;
        public BudgetController()
        {
            _connection = new MySqlConnection("Server=mariadb;User ID=root;Password=root;Database=domestique");
            _connection.Open();

            var creation =
                _connection.CreateCommand();
            creation.CommandText = "CREATE TABLE IF NOT EXISTS depenses " +
                    "(id INT NOT NULL AUTO_INCREMENT, nom text NOT NULL, PRIMARY KEY (id))";
            creation.ExecuteNonQuery();
        }
    
        [HttpGet(Name = "GetBudget")]
        public IEnumerable<Budget> Get()
        {
            var req = _connection.CreateCommand();
            req.CommandText = "SELECT id, nom FROM depenses";
            var reader = req.ExecuteReader();
            var liste = new List<Budget>();
            while (reader.Read())
            {
                var b = new Budget
                {
                    Id = reader.GetInt32(0),
                    Nom = reader.GetString(1)
                };
                liste.Add(b);
            }

            return liste;
        }
        
        
        [HttpPost(Name = "PostBudget")]
        public Budget Post(Budget budget)
        {
            var req = _connection.CreateCommand();
            req.CommandText = "INSERT INTO depenses(nom) VALUES (@nom)";
            req.Parameters.AddWithValue("@nom", budget.Nom);
            req.ExecuteNonQuery();
            budget.Id = req.LastInsertedId;
            return budget;
        }
    }
}